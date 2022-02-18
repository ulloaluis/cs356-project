import json

from observatory_config import *
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


def average_score_analysis(results):
    """
    Get the average Mozilla Observatory score for the specified group.
    """
    count = 0
    running_sum = 0
    for domain, result in results.items():
        if len(result["observatory_result"]) == 0:
            continue
        count += 1
        running_sum += result["observatory_result"]["score"]
    print(f"Average score: {running_sum / count:.3f}")
    print("-"*50, "\n")


def merge_dicts(d1, d2):
    merged = d1.copy()
    merged.update(d2)
    return merged


def get_results(filename):
    with open(filename) as f:
        return json.load(f)


def popular_vs_longtail_analysis():
    top_results = get_results(TOP_RESULTS_FILE)
    longtail_results = get_results(LONGTAIL_RESULTS_FILE)

    print("Spearman Correlation Analysis: Top Sites")
    spearman_correlation_analysis(top_results)
    print("Spearman Correlation Analysis: Longtail Sites")
    spearman_correlation_analysis(longtail_results)
    print("Spearman Correlation Analysis: Top & Longtail Sites Merged")
    spearman_correlation_analysis(merge_dicts(top_results, longtail_results))

    print("Average score: Top Sites")
    average_score_analysis(top_results)
    print('Average score: Longtail Sites')
    average_score_analysis(longtail_results)
    print("Average score: Top & Longtail Sites Merged")
    average_score_analysis(merge_dicts(top_results, longtail_results))


def random_subset_analysis():
    results = get_results(RANDOM_SUBSET_FILE)
    print(f"Random sample of {SAMPLE_SIZE} from range {RANK_RANGE['min']} - {RANK_RANGE['max']}")

    print("Spearman Correlation Analysis")
    spearman_correlation_analysis(results)

    print("Average Score Analysis")
    average_score_analysis(results)


if __name__ == "__main__":
    if ANALYSIS_TYPE == AnalysisType.POPULAR_VS_LONGTAIL:
        popular_vs_longtail_analysis()
    elif ANALYSIS_TYPE == ANALYSIS_TYPE.RANDOM_SUBSET:
        random_subset_analysis()
