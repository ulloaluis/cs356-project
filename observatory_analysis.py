import json

from collections import defaultdict
from observatory_config import *
from scipy import stats
from utils import *
import requests


def spearman_correlation_analysis(results):
    """
    Use Spearman Rank Correlation coefficient to summarize the
    relationship between Trancos Popularity Rank and Mozilla Observatory Score
    for a particular group.
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
    """
    ranks, scores = [], []
    for domain, result in results.items():
        if len(result["observatory_assessment"]) == 0:
            # print(f"Domain \'{domain}\' has no observatory data, skipping...")
            continue
        ranks.append(result["trancos_rank"])
        scores.append(result["observatory_assessment"]["score"])
    
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
        if len(result["observatory_assessment"]) == 0:
            continue
        count += 1
        running_sum += result["observatory_assessment"]["score"]
    print(f"Average score: {running_sum / count:.3f}")
    print("-"*50, "\n")


def popular_vs_longtail_analysis():
    top_results = get_results(TOP_RESULTS_FILE)
    longtail_results = get_results(LONGTAIL_RESULTS_FILE)

    print("Average score: Top Sites")
    average_score_analysis(top_results)
    print('Average score: Longtail Sites')
    average_score_analysis(longtail_results)

    tests = [{
        "name": test, 
        "expectation": details['expectation'],
        } for test, details in top_results[list(top_results)[0]]["observatory_tests"].items()]

    # Collection information about each group for each test.
    test_analysis = {}
    for test in tests:
        test_name = test["name"]
        test_expectation = test["expectation"]

        # Frequency of top and longtail for each test.
        test_analysis[test_name] = {"top": 0, "longtail": 0}
        for _, domain_data in top_results.items():
            passed_test = domain_data["observatory_tests"][test_name]["pass"]
            test_analysis[test_name]["top"] += (int)(passed_test)
        for _, domain_data in longtail_results.items():
            passed_test = domain_data["observatory_tests"][test_name]["pass"]
            test_analysis[test_name]["longtail"] += (int)(passed_test)

        print(f"Test: {test_name}")
        print(f"\tExpectation: {test_expectation}")
        tfreq = 100 * test_analysis[test_name]['top'] / len(top_results)
        print(f"\tTop group freq:\t\t {tfreq:.2f}% ({test_analysis[test_name]['top']} / {len(top_results)})")
        lfreq = 100 * test_analysis[test_name]['longtail'] / len(longtail_results)
        print(f"\tLongtail group freq:\t {lfreq:.2f}% ({test_analysis[test_name]['longtail']} / {len(longtail_results)})")


def random_subset_analysis():
    results = get_results(RANDOM_SUBSET_FILE)
    print(len(results))
    print(f"Random sample of {SAMPLE_SIZE} from range {RANK_RANGE['min']} - {RANK_RANGE['max']}")

    # Correlation
    print("Spearman Correlation Analysis")
    spearman_correlation_analysis(results)

    # Average Score
    print("Average Score Analysis")
    average_score_analysis(results)

    # Performance by different types of servers
    server_to_count = defaultdict(int)
    server_to_running_score = defaultdict(int)
    for domain, data in results.items():
        resp_headers = data['observatory_assessment']['response_headers']
        if 'server' in resp_headers:
            server = resp_headers['server'].lower().strip()
        else:
            server = ''
        server_to_count[server] += 1
        server_to_running_score[server] += data['observatory_assessment']['score']
    
    for server, count in server_to_running_score.items():
        server_to_running_score[server] /= server_to_count[server]
    
    sorted_by_freq = sorted(server_to_count.items(), key=lambda item: item[1], reverse=True)
    for server, freq in sorted_by_freq:
        score = server_to_running_score[server]
        # Ignore anything that only shows up once
        if freq > 5:
            print(f"{server}: {score:.2f} ({freq})")

    print(server_to_count)
    print(server_to_running_score)


if __name__ == "__main__":
    if ANALYSIS_TYPE == AnalysisType.POPULAR_VS_LONGTAIL:
        popular_vs_longtail_analysis()
    elif ANALYSIS_TYPE == ANALYSIS_TYPE.RANDOM_SUBSET:
        random_subset_analysis()
