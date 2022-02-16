import os

OBSERVATORY_URL = "https://http-observatory.security.mozilla.org/api/v1"
SAMPLE_SIZE = 250
PROCESS_RESULTS_DELAY_SECONDS = 60

RESULTS_DIRECTORY = f"{os.getcwd()}/results"
TOP_RESULTS_FILENAME = "top_sites_results.json"
LONGTAIL_RESULTS_FILENAME = "longtail_sites_results.json"

