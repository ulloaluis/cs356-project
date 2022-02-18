import os

from enum import Enum
class AnalysisType(Enum):
    # Perform top 10,000 vs longtail 990,000 data collection / analysis
    POPULAR_VS_LONGTAIL = 1
    # Perform data collection / analysis over specified subset of dataset
    # e.g. if we want to get a uniform random score distribution over top 1M
    RANDOM_SUBSET = 2

# Used by all analysis types
OBSERVATORY_URL = "https://http-observatory.security.mozilla.org/api/v1"
RESULTS_DIRECTORY = f"{os.getcwd()}/subset_results_sample_1000_from_top_1000000"
PROCESS_RESULTS_DELAY_SECONDS = 60

# Used by POPULAR_VS_LONGTAIL analysis
SAMPLE_SIZE = 1000
TOP_RESULTS_FILE = os.path.join(RESULTS_DIRECTORY, "top_sites_results.json")
LONGTAIL_RESULTS_FILE = os.path.join(RESULTS_DIRECTORY, "longtail_sites_results.json")

# Used by RANDOM_SUBSET analysis
RANK_RANGE = {
    'min': 1,
    'max': 1000000
}
RANDOM_SUBSET_FILE = os.path.join(RESULTS_DIRECTORY, "results.json")

# Specify analysis type for observatory.py (data collection)
# and observatory_analysis.py  (analysis)
ANALYSIS_TYPE =  AnalysisType.RANDOM_SUBSET