import requests
from bs4 import BeautifulSoup
import concurrent.futures
import logging
import urllib.parse
import argparse
from urllib.parse import urlparse, urljoin
import warnings
from datetime import datetime

start_time = datetime.now()
formatted_start_time = start_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
print(f"Initializing crawling: {formatted_start_time}")

EXCLUDE_EXTENSIONS = [".jpg", ".png", ".gif", ".pdf"]

def add_to_queue(url, visited, queue):
    if url not in visited and url not in queue:
        queue.append(url)

def process_link(url, visited, session, headers, timeout, domains, queue):
    if url in visited:
        return

    visited.add(url)

    try:
        response = session.get(url, headers=headers, timeout=timeout, allow_redirects=False)
        if response.is_redirect:
            redirect_url = response.headers['Location']
            url = urljoin(url, redirect_url)

        soup = BeautifulSoup(response.content, "html.parser")

        for link in soup.find_all("a"):
            href = link.get("href")
            if href:
                try:
                    url_obj = urllib.parse.urlparse(href)
                    if not url_obj.scheme:
                        href = urllib.parse.urljoin(url, href)
                        url_obj = urllib.parse.urlparse(href)
                    if domains not in href:
                        continue
                    if any(ext in href for ext in EXCLUDE_EXTENSIONS):
                        continue
                    href = urllib.parse.urlunparse(url_obj)
                    if href not in visited:
                        add_to_queue(href, visited, queue)
                except Exception as e:
                    logging.error(f"Error processing link {href} on {url}: {str(e)}")

    except Exception as e:
        logging.error(f"{url} failed with error: {str(e)}")

def start_crawler(base_url, domains=None, exclude_keywords=None, headers=None, timeout=30, user_agent=None, max_threads=10, max_redirects=50):
    logging.info("Starting crawler...")
    print("--> Crawled URLs are in links.txt")
    visited = set()
    queue = []
    errors = []
    url_count = 0

    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=30, pool_maxsize=50, max_retries=max_redirects)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    session.headers.update({"User-Agent": user_agent})

    add_to_queue(base_url, visited, queue)

    while queue:
        threads = min(max_threads, len(queue))
        batch = [queue.pop(0) for _ in range(threads)]

        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_url = {executor.submit(process_link, url, visited, session, headers, timeout, domains, queue): url for url in batch}

            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    future.result()
                    logging.info(f"Crawled successfully {url}")
                    url_count += 1

                    print("    --> Count = {}".format(url_count), end='\r')
                    with open("links.txt", 'a') as fd:
                        fd.write(url + '\n')
                except Exception as e:
                    logging.exception(f"Failed to crawl {url}. Reason: {e}")

    end_time = datetime.now()
    formatted_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    time_taken = end_time - start_time
    print(f"\nCrawling completed: {formatted_end_time}")
    print(f"Time taken: {time_taken}")

class CustomHTTPAdapter(requests.adapters.HTTPAdapter):
    def __init__(self, max_redirects=30, *args, **kwargs):
        self.max_redirects = max_redirects
        super().__init__(*args, **kwargs)

    def get_redirect_target(self, request, response):
        location = response.headers['Location']
        return urljoin(request.url, location)

    def get_environ_proxies(self, url):
        return super().get_environ_proxies(url)

    def should_strip_auth(self, prepped_request):
        return super().should_strip_auth(prepped_request)

    def should_follow_redirects(self, response):
        return super().should_follow_redirects(response) and self.max_redirects > 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script description')
    parser.add_argument('--target', help='Target URL')
    parser.add_argument('--threads', type=int, default=10, help='Number of threads (default is 10)')
    parser.add_argument('--timeout', type=int, default=30, help='Timeout for requests in seconds (default is 30)')
    parser.add_argument('--max_redirects', type=int, default=30, help='Maximum redirection to follow (default is 50)')
    parser.add_argument('--verbose', type=str, default="false", help='Display verbose error & warning message (default is disables)')
    args = parser.parse_args()
    target = args.target
    threads = args.threads
    timeout = args.timeout
    max_redirects = args.max_redirects

    parsed_url = urlparse(target)
    main_domain = parsed_url.netloc

    subdomains = main_domain.split('.')
    domain = ".".join(subdomains[-2:])

    if args.verbose.lower() == "true":
        logging.basicConfig(level=logging.WARNING)
    else:
        null_handler = logging.NullHandler()
        logging.getLogger().addHandler(null_handler)
        warnings.filterwarnings("ignore", category=UserWarning, module="bs4")

    start_crawler(base_url=target, domains=domain, max_threads=threads, timeout=timeout, max_redirects=max_redirects)

