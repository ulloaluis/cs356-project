from observatory_constants import *
from scipy import stats


def spearman_correlation_analysis(results):
    """
    Use Spearman Rank Correlation coefficient to summarize the
    relationship between Trancos Popularity Rank and Mozilla Observatory Score
    for a particular group.
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
    """
    print("Spearman Correlation Analysis: Trancos Rank vs Observatory Score")

    for domain, result in results:



def merge_dicts(d1, d2):
    merged = d1.copy()
    merged.update(d2)
    return merged


def get_results(filename):
    with open(filename) as f:
        return json.load(f)


if __name__ == "__main__":
    top_results = get_results(TOP_RESULTS_FILENAME)
    longtail_results = get_results(LONGTAIL_RESULTS_FILENAME)

    print("Spearman Correlation Analysis: Top Sites")
    spearman_correlation_analysis(top_results)
    print("Spearman Correlation Analysis: Longtail Sites")
    spearman_correlation_analysis(longtail_results)
    print("Spearman Correlation Analysis: Top & Longtail Sites Merged")
    spearman_correlation_analysis(merge_dicts(top_results, longtail_results))

