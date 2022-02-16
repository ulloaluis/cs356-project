import json

from observatory_constants import *
from scipy import stats


def spearman_correlation_analysis(results):
    """
    Use Spearman Rank Correlation coefficient to summarize the
    relationship between Trancos Popularity Rank and Mozilla Observatory Score
    for a particular group.
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
    """
    ranks, scores = [], []
    for domain, result in results.items():
        if len(result["observatory_result"]) == 0:
            # print(f"Domain \'{domain}\' has no observatory data, skipping...")
            continue
        ranks.append(result["trancos_rank"])
        scores.append(result["observatory_result"]["score"])
    
    print(f"{len(scores)} out of {len(results)} sites have valid observatory data.")

    spearman_result = stats.spearmanr(ranks, scores)
    print(spearman_result)
    print("-"*50, "\n")


def merge_dicts(d1, d2):
    merged = d1.copy()
    merged.update(d2)
    return merged


def get_results(filename):
    with open(filename) as f:
        return json.load(f)


if __name__ == "__main__":
    top_results = get_results(TOP_RESULTS_FILE)
    longtail_results = get_results(LONGTAIL_RESULTS_FILE)

    print("Spearman Correlation Analysis: Top Sites")
    spearman_correlation_analysis(top_results)
    print("Spearman Correlation Analysis: Longtail Sites")
    spearman_correlation_analysis(longtail_results)
    print("Spearman Correlation Analysis: Top & Longtail Sites Merged")
    spearman_correlation_analysis(merge_dicts(top_results, longtail_results))
