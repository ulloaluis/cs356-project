"""
Uses the Mozilla Observatory API to get security scans on a sample
of the top sites (top 10,000) and longtail sites (everything else)
in the Trancos Top 1M dataset.


Note that calling initiate_domain_scan() only has to happen once for a domain
in the past 24 hours in order for get_scan_result() to return a value. Common
error cases are when the site is down for maintenance when the scan was requested.
"""
import json
import requests
import time
import threading
import traceback

import numpy as np
import pandas as pd

from io import TextIOWrapper
from observatory_config import *
from utils import *
from zipfile import ZipFile


# For reproducibility
rng = np.random.default_rng(seed=12345)


def get_test_scan_results(domain, scan_id):
    """Returns json from scanning tests endpoint, or None if the scan failed."""
    max_retry = 5
    while True:
        max_retry -= 1
        if max_retry <= 0:
            return None
        try:
            resp = requests.get(f"{OBSERVATORY_URL}/getScanResults", params={"scan": scan_id})
            resp.raise_for_status()
            if "error" in resp.json() or resp.status_code != 200:
                time.sleep(0.5)
                continue
            results = resp.json()
            return results
        except requests.HTTPError:
            # Report errors and try again
            print(f"Error polling {domain} (scan: {scan_id}), retrying...")
            traceback.print_exc()
            time.sleep(0.5)  # Wait before retry if error or not finished yet


def get_analyze_scan_results(domain):
    """Returns the json result from scanning the domain, or None if the scan failed."""
    max_retry = 5
    while True:
        max_retry -= 1
        if max_retry <= 0:
            return None

        try:
            resp = requests.get(f"{OBSERVATORY_URL}/analyze", params={"host": domain})
            resp.raise_for_status()
            parsed = resp.json()
            if "state" in parsed and parsed["state"] == "FINISHED":
                return parsed
            elif "state" in parsed and parsed["state"] in ["ABORTED", "FAILED"]:
                time.sleep(0.5)
                continue
            else:
                time.sleep(0.5)
                continue
        except requests.HTTPError:
            # Report errors and try again
            print(f"Error polling {domain}, retrying...")
            traceback.print_exc()
            time.sleep(0.5)  # Wait before retry if error or not finished yet


def retrieve_scan_data(sites, domain):
    """
    Returns: dict in the following format
        dict[domain] = {
            trancos_rank = /* trancos rank on site */
            observatory_assessment = /* entire json/dict returned from observatory assessment scan,
                                     dict[observatory_assessment][score] for observatory score */
            observatory_tests = /* json/dict returned from observatory tests scan */
        }
    """
    print(f"Scanning {domain}...")
    assessment = get_analyze_scan_results(domain)
    if assessment != None:
        tests = get_test_scan_results(domain, assessment["scan_id"])
    else:
        print(f"WARNING: {domain} failed assessment scan. Skipping...")
        return None

    if tests == None:
        print(f"WARNING: {domain} failed tests retrieval scan. Skipping...")
        return None

    sample_row = sites.loc[sites.domain == domain]
    return {
        "observatory_assessment" : assessment,
        "observatory_tests" : tests,
        "trancos_rank" : int(sample_row.ranking)
    }


def initiate_domain_scan(domain):
    """Initiates a scan of the domain."""
    print(f"Initiating scan of {domain}...")
    resp = requests.post(
        f"{OBSERVATORY_URL}/analyze",
        params={"host": domain},
        data={"hidden": "true"},
    )
    valid = "error" not in resp.json() and resp.status_code == 200
    if not valid:
        print(f"...{domain} scan failed.")
    return valid


def sample_n(sites, n, query):
    return (sites.query(query)
            .sample(n=n, random_state=rng))


def get_observatory_data(sites, n, query, group_results):
    """
    Will find `n` valid domains conforming to the constraints specified by
    `query` in `sites.

    Returns dict of Observatory data as described in `retrieve_scan_data`
    """
    print(f"Getting observatory data for `{n}` domains under query `{query}`...")
    while (len(group_results) < n):
        # Pessimistically over sample by 30% to avoid long wait times
        # associated with having to resample after failed connections.
        sample_size_extra = (n - len(group_results))
        sample_size_extra += (int)(0.3 * sample_size_extra)
        group = sample_n(sites, sample_size_extra, query)

        # Drop sampled group from sites to prevent resampling domains.
        sites = sites.drop(group.index)

        if len(group) == 0:
            print(f"WARNING: ran out of domains to sample. got {len(group_results)} out of {n}")
            exit()

        maybe_valid_domains = []
        for domain in group.domain:
            is_valid_domain = initiate_domain_scan(domain)
            if is_valid_domain:
                maybe_valid_domains.append(domain)
            # else: domain is invalid and gets excluded
        
        print(f"Waiting {PROCESS_RESULTS_DELAY_SECONDS} seconds for scans to complete...")
        time.sleep(PROCESS_RESULTS_DELAY_SECONDS)

        for domain in maybe_valid_domains:
            # We pass 'groups' instead of 'sites' because 'sites' no longer
            # contains data for 'groups,' and this method will access trancos
            # rank associated with the domain.
            data = retrieve_scan_data(group, domain)
            if data != None:
                if len(group_results) == n:
                    break
                group_results[domain] = data

    if len(group_results) != n:
        print(f"ERROR: expected {n} domains got {len(group_results)}") 
        exit()
    
    print(f"...group scan for `{n}` domains with query `{query}` successful.")
    return group_results


def get_sites():
    with ZipFile("tranco_36PL-1m.csv.zip").open("top-1m.csv") as f:
        sites = pd.read_csv(TextIOWrapper(f), header=None, names=["ranking", "domain"])
    assert sites.ranking.iloc[0] == 1
    assert sites.ranking.iloc[-1] == 1_000_000
    assert len(sites) == 1_000_000
    return sites


class GetObservatoryDataThread(threading.Thread):
    def __init__(self, sites, sample_size, query, results):
        threading.Thread.__init__(self)
        self.sites = sites
        self.sample_size = sample_size
        self.query = query
        self.results = results
    
    def run(self):
        get_observatory_data(
            self.sites, self.sample_size, self.query, self.results)


def popular_vs_longtail_data_collection(sites):
    print("Popular vs. Longtail data collection.")

    # Run each group in a separate thread, since there's a lot of idle
    # waiting associated with Observatory's API.
    top_results = {}
    top_group_thread = GetObservatoryDataThread(
        sites.copy(), SAMPLE_SIZE_TOP, "ranking <= 10_000", top_results)

    longtail_results = {}
    longtail_group_thread = GetObservatoryDataThread(
        sites.copy(), SAMPLE_SIZE_LONGTAIL, "ranking > 10_000", longtail_results)

    top_group_thread.start()
    longtail_group_thread.start()

    top_group_thread.join()
    longtail_group_thread.join()

    overwrite_file(top_results, TOP_RESULTS_FILE)
    overwrite_file(longtail_results, LONGTAIL_RESULTS_FILE)


def random_subset_data_collection(sites):
    print(f"Random subset data collection.")
    print(f"Rank range: [{RANK_RANGE['min']}-{RANK_RANGE['max']}]")

    subset_results = {}
    get_observatory_data(
        sites.copy(), SAMPLE_SIZE,
        f"ranking >= {RANK_RANGE['min']} & ranking < {RANK_RANGE['max']}",
        subset_results
    )

    overwrite_file(subset_results, RANDOM_SUBSET_FILE)


if __name__ == "__main__":
    """
    Initiates group scans, waits for some time, and then processes the results.

    Since the observatory API requires you to first initiate the scan before
    then retrieving the results, this is designed to initiate as many scans
    as possible before attempting to retrieve any results.
    """
    sites = get_sites()
    if ANALYSIS_TYPE == AnalysisType.POPULAR_VS_LONGTAIL:
        popular_vs_longtail_data_collection(sites)
    elif ANALYSIS_TYPE == ANALYSIS_TYPE.RANDOM_SUBSET:
        random_subset_data_collection(sites)
