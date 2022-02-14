from io import TextIOWrapper
from zipfile import ZipFile

import numpy as np
import pandas as pd

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
