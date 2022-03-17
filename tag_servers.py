from itertools import islice
import requests
import threading
from observatory_config import *
from utils import *


FILE_TO_TAG = RANDOM_SUBSET_FILE

class ServerQueryingThread(threading.Thread):
    def __init__(self, results, thread_id):
        threading.Thread.__init__(self)
        self.results = results
        self.thread_id = thread_id
        print(f"Thread {self.thread_id} was assigned {len(self.results)} items")
    
    def run(self):
        for i, (domain, data) in enumerate(self.results.items()):
            if i % 50 == 0:
                print(f"Thread {self.thread_id} is {((i+1)/len(self.results))*100:.2f}% complete.")

            resp_headers = data['observatory_assessment']['response_headers']
            if 'server' not in resp_headers:
                try:
                    response = requests.get(f"http://{domain}", timeout=2)
                    if 'Server' in response.headers:
                        server = response.headers['Server']
                        self.results[domain]['observatory_assessment']['response_headers']['server'] = server
                except:
                    continue
            

def main():
    results = get_results(FILE_TO_TAG)

    num_threads = 8
    chunk_size = int(len(results) / num_threads) + 1
    it = iter(results)
    threads = []
    for thread_id in range(num_threads):
        thread_results = {k: results[k] for k in islice(it, chunk_size)}
        threads.append(ServerQueryingThread(thread_results, thread_id))

    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    modified_results = dict()
    for thread in threads:
        modified_results.update(thread.results)

    overwrite_file(modified_results, FILE_TO_TAG + '-temp')

if __name__ == '__main__':
    main()
