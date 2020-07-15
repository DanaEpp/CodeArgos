#!/usr/bin/env python3
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re
import sys
from urllib.parse import urlparse,urljoin
from bs4 import BeautifulSoup
from pprint import pprint
import signal
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
import logging
import time
from codeargos.datastore import DataStore
from codeargos.scrapedpage import ScrapedPage

class Scraper:

    allowed_content = (
        'text/plain', 
        'text/html', 
        'text/javascript', 
        'application/x-httpd-php',
        'application/xhtml+xml'
        )

    def __init__(self, url):
        self.url = url 
        self.internal_urls = None
        self.content = None

    def get_page(self, session, url):

        try:
            head = session.head(url)
            if head.status_code == 200:
                content_type = head.headers.get('Content-Type')

                if content_type.startswith(self.allowed_content):
                    page = session.get(url)
                    parsed_html = BeautifulSoup(page.content, features='html.parser')
                else:
                    return ""
            else:
                return ""
        except Exception as ex:

            logging.exception(ex)
            return ""
        return parsed_html

    def get_links(self, url, parsed_html):

        links = []

        for link in parsed_html.find_all("a", href=True):
            link_url = link.get('href').strip()
            if link_url is None:
                continue

            parsed_link = urlparse(link_url)

            # Need to account for malformed URLs, ie: http:/singleslashisbad.com
            if parsed_link.scheme and not parsed_link.netloc:
                continue
            elif not parsed_link.scheme and not parsed_link.netloc and parsed_link.path:
                full_url = urljoin(url, link_url)
            else:
                full_url = link_url

            links.append( full_url )

        return links    

    def scrape(self):
        session = requests.session()

        # Add incrimental backoff retry logic some we aren't slamming servers
        retry_strategy = Retry(
            total=10,
            status_forcelist=[104,429,500,502,503,504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        parsed_html = self.get_page(session, self.url)        
        if len(parsed_html) > 0:
            scraped_urls = self.get_links(self.url, parsed_html)
        else:
            scraped_urls = []
            
        # TODO: Add script block parser and dump results into self.content

        session.close()

        self.internal_urls = set(scraped_urls)

        return self.internal_urls, self.url, self.content

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
