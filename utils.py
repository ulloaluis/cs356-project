import json

def debug(data):
    for domain, result in data.items():
        print(f"Domain: {domain}")
        print(f"Score: {result['observatory_assessment']['score']}")        
        for test, details in result["observatory_tests"].items():
            print(f"Test: {test}")
            for k, v in details.items():
                print(f"\t{k}: {v}")
            print()


def get_results(filename):
    with open(filename) as f:
        return json.load(f)


def merge_dicts(d1, d2):
    merged = d1.copy()
    merged.update(d2)
    return merged


def overwrite_file(results, filename):
    # Note: directory must already exist!
    print("Writing to file:", filename)
    with open(filename, 'w+') as f:
        json.dump(results, f)
