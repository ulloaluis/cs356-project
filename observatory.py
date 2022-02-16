"""
Uses the Mozilla Observatory API to get security scans on a sample
of the top sites (top 10,000) and longtail sites (everything else)
in the Trancos Top 1M dataset.


Note that calling initiate_domain_scan() only has to happen once for a domain
in the past 24 hours in order for get_scan_result() to return a value. Common
error cases are when the site is down for maintenance when the scan was requested.
"""
import json
import os
import requests
import time
import traceback

import numpy as np
import pandas as pd

from io import TextIOWrapper
from observatory_constants import *
from zipfile import ZipFile


# For reproducibility
rng = np.random.default_rng(seed=12345)


def overwrite_file(results, filename):
    print("Writing to file:", filename)
    with open(filename, 'w+') as f:
        json.dump(results, f)


def get_scan_result(domain):
    """Returns the json result from scanning the domain, or empty dict if the scan failed."""
    while True:
        try:
            resp = requests.get(f"{OBSERVATORY_URL}/analyze", params={"host": domain})
            resp.raise_for_status()
            parsed = resp.json()
            if "state" in parsed and parsed["state"] == "FINISHED":
                return parsed
            elif "state" in parsed and parsed["state"] in ["ABORTED", "FAILED"]:
                print(f"Scan failed for {domain}")
                print(f"Response: {resp.text}")
                return {}
            else:
                print(f"Scan failed for {domain}")
                print(f"Response json: {parsed}")
                return {}
        except requests.HTTPError:
            # Report errors and try again
            print(f"Error polling {domain}, retrying...")
            traceback.print_exc()
        time.sleep(0.5)  # Wait before retry if error or not finished yet


def process_group_results(group):
    """
    Returns: dict in the following format
        dict[domain] = {
            trancos_rank = /* trancos rank on site */
            observatory_result = /* entire json/dict returned from observatory scan,
                                     dict[observatory_result][score] for observatory score */
        }
    """
    group_results = {}
    for domain in group.domain:
        print(f"Scanning {domain}...")
        result = get_scan_result(domain)
        sample_row = group.loc[group.domain == domain]
        group_results[domain] = {
            "observatory_result" : result,
            "trancos_rank" : int(sample_row.ranking)
        }
    return group_results


def initiate_domain_scan(domain):
    """Initiates a scan of the domain."""
    print(f"Initiating scan of {domain}...")
    resp = requests.post(
        f"{OBSERVATORY_URL}/analyze",
        params={"host": domain},
        data={"hidden": "true"},
    )
    resp.raise_for_status()
    print("***", resp.text)


def initiate_group_scan(group):
    for domain in group.domain:
        initiate_domain_scan(domain)


def get_sites():
    with ZipFile("tranco_36PL-1m.csv.zip").open("top-1m.csv") as f:
        sites = pd.read_csv(TextIOWrapper(f), header=None, names=["ranking", "domain"])
    assert sites.ranking.iloc[0] == 1
    assert sites.ranking.iloc[-1] == 1_000_000
    assert len(sites) == 1_000_000
    return sites


if __name__ == "__main__":
    """
    Since the observatory API requires you to first initiate the scan before
    then retrieving the results, this is designed to initiate as many scans
    as possible before attempting to retrieve any results.

    Initiates top group scans and longtail scans, wait for some time, and
    then process the results.
    """
    sites = get_sites()

    print(f"Initiating top sites group scan...")
    top_group = (
        sites.query("ranking <= 10_000")
        .sample(n=SAMPLE_SIZE, random_state=rng)
        .reset_index(drop=True)
    )
    initiate_group_scan(top_group)
    print('\n', "-"*30,)

    print(f"Initiating longtail sites group scan...")
    longtail_group = (
        sites.query("ranking > 10_000")
        .sample(n=SAMPLE_SIZE, random_state=rng)
        .reset_index(drop=True)
    )
    initiate_group_scan(longtail_group)
    print('\n', "-"*30,)

    print(f"Waiting {PROCESS_RESULTS_DELAY_SECONDS} seconds for scans to complete...")
    time.sleep(PROCESS_RESULTS_DELAY_SECONDS)

    print(f"Processing top sites group results...")
    top_results = process_group_results(top_group)
    overwrite_file(
        top_results,
        os.path.join(RESULTS_DIRECTORY, TOP_RESULTS_FILENAME))
    print('\n', "-"*30,)

    print(f"Processing longtail sites group results...")
    longtail_results = process_group_results(longtail_group)
    overwrite_file(
        longtail_results,
        os.path.join(RESULTS_DIRECTORY, LONGTAIL_RESULTS_FILENAME))
    print('\n', "-"*30,)

