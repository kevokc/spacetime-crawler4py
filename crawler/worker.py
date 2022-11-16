from threading import Thread
from urllib.parse import urlparse
from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time

class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests from scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)

        print("Number of unique pages found:", str(len(scraper.Uniques)))
        print("Longest page:", scraper.LongestPage, "with word count of", scraper.LongestWordCount)
        scraper.MCW.sort(key=lambda x:x[1], reverse=True)
        print("50 most common words:", scraper.MCW[:50])
            
        scraper.Subdomains.clear()
        for i in scraper.Uniques:
            parsed = urlparse(i)
            if ".ics.uci.edu" in parsed.netloc.lower():
                scraper.Subdomains[parsed.hostname] = scraper.Subdomains.get(parsed.hostname, 0) + 1
        lts = list(scraper.Subdomains.items())
        lts.sort(key=lambda x:x[0])
        print("Subdomains:")
        for k, v in lts:
            print(str(k) + ", " + str(v))
