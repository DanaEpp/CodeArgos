#!/usr/bin/env python3
import re
import sys
import signal
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
import logging
import time
from codeargos.scraper import Scraper
from codeargos.datastore import DataStore
from codeargos.scrapedpage import ScrapedPage

class WebCrawler:
    def __init__(self, seed_url, threads, stats):
        self.seed_url = seed_url
        self.pool = ThreadPoolExecutor(max_workers=threads)
        self.processed_urls = set([])
        self.queued_urls = Queue()
        self.queued_urls.put(self.seed_url)
        self.data = {}
        self.show_stats = stats
        self.data_store = DataStore("codeargos")
        signal.signal(signal.SIGINT, self.dump_data)

    def dump_data(self, signal, frame):
        choice = input( "\nEarly abort detected. Dump data already collected? (to processed.txt): [y/N] ")
        choice = choice.lower()
        if choice == 'y':
            with open('processed.txt', 'w') as f:
                for item in self.processed_urls:
                    f.write("%s\n" % item)
        sys.exit()

    def process_scraper_results(self, future):
        # get the items of interest from the future object
        internal_urls, url, content = future._result[0], future._result[1], future._result[2]

        # assign scraped script blocks
        self.data[url] = content

        # also add scraped links to queue if they
        # aren't already queued or already processed
        for link_url in internal_urls:
            if link_url.startswith(self.seed_url):
                if link_url not in self.queued_urls.queue and link_url not in self.processed_urls:
                    self.queued_urls.put(link_url)

    def processed(self):
        return len(self.processed_urls)

    def start(self):
        LOG_EVERY_N = 500
        i = 0
        
        while True:
            try:
                # get a url from the queue
                target_url = self.queued_urls.get(timeout=10)

                # check that the url hasn't already been processed
                if target_url not in self.processed_urls:
                    # add url to the processed list
                    self.processed_urls.add(target_url)

                    logging.debug(f'[URL] {target_url}')

                    job = self.pool.submit(Scraper(target_url).scrape)
                    job.add_done_callback(self.process_scraper_results)

                if self.show_stats:
                    if i % LOG_EVERY_N == 0:
                        print("Processed: {0:<8} | Queue: {1:<8} | Scheduled Jobs: {2:<8}".format(
                            len(self.processed_urls), 
                            self.queued_urls.qsize(),
                            self.pool._work_queue.qsize()))                    
                i=i+1
            except Empty:
                logging.debug("All queues and jobs complete.")
                break
            except Exception as e:
                print(e)
