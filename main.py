import time
import traceback
from io import TextIOWrapper
from zipfile import ZipFile

import numpy as np
import pandas as pd
import requests

# For reproducibility
rng = np.random.default_rng(seed=12345)

with ZipFile("tranco_36PL-1m.csv.zip").open("top-1m.csv") as f:
    sites = pd.read_csv(TextIOWrapper(f), header=None, names=["ranking", "domain"])
assert sites.ranking.iloc[0] == 1
assert sites.ranking.iloc[-1] == 1_000_000
assert len(sites) == 1_000_000

# Sample 250 from each group (top 10k, and next 990k)
top_sites = (
    sites.query("ranking <= 10_000")
    .sample(n=250, random_state=rng)
    .reset_index(drop=True)
)
long_tail_sites = (
    sites.query("ranking > 10_000")
    .sample(n=250, random_state=rng)
    .reset_index(drop=True)
)

print(top_sites)
print(long_tail_sites)

observatory_url = "https://http-observatory.security.mozilla.org/api/v1"


def initiate_scan(domain):
    """Initiates a scan of the domain."""
    resp = requests.post(
        f"{observatory_url}/analyze",
        params={"host": domain},
        data={"hidden": "true"},
    )
    resp.raise_for_status()
    print("***", resp.text)


def poll_scan_result(domain):
    """Returns the score of the scanning the domain, or None if the scan failed."""
    while True:
        try:
            resp = requests.get(f"{observatory_url}/analyze", params={"host": domain})
            resp.raise_for_status()
            parsed = resp.json()
            if parsed["state"] == "FINISHED":
                return parsed["score"]
            elif parsed["state"] in ["ABORTED", "FAILED"]:
                print(f"Scan failed for {domain}")
                print(resp.text)
                return None
        except requests.HTTPError:
            # Report errors and try again
            print(f"Error polling {domain}, retrying...")
            traceback.print_exc()
        time.sleep(0.5)  # Wait before retry if error or not finished yet


domains = long_tail_sites.domain.sample(n=10)
for domain in domains:
    print(f"Initiating scan of {domain}...")
    initiate_scan(domain)
for domain in domains:
    print(f"Scanning {domain}...")
    score = poll_scan_result(domain)
    print(f"{domain=} {score=}")
