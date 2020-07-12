#!/usr/bin/env python3
import requests
import re
import sys
from urllib.parse import urlparse,urljoin
from bs4 import BeautifulSoup
from pprint import pprint
import signal

class WebCrawler(object):

    allowed_content = (
        'text/plain', 
        'text/html', 
        'text/javascript', 
        'application/x-httpd-php',
        'application/xhtml+xml'
        )

    def __init__(self, starting_url):
        self.starting_url = starting_url
        self.visited = set()
        self.crawl_list = [starting_url]
        signal.signal(signal.SIGINT, self.dump_data)

    def dump_data(self, signal, frame):
        with open('visited.txt', 'w') as f:
            for item in self.visited:
                f.write("%s\n" % item)
        with open('links.txt', 'w') as f2:
            for item in self.crawl_list:
                f2.write("%s\n" % item)
        sys.exit()

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
            print(ex)
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

            if full_url.startswith(self.starting_url): 
                if full_url not in links: 
                    if full_url not in self.visited:
                        if full_url not in self.crawl_list:
                            links.append( full_url )

        return links    
    
    def crawl(self, url):
        LOG_EVERY_N = 500
        i = 0

        session = requests.session()

        while self.crawl_list:
            url_to_crawl = self.crawl_list.pop()
            if url_to_crawl in self.visited:
                continue

            self.visited.add(url_to_crawl)
            if i % LOG_EVERY_N == 0:
                print("Pages: {0}. Que: {1}".format(self.total_pages(), len(self.crawl_list)))
            i=i+1

            parsed_html = self.get_page(session, url_to_crawl)
            if len(parsed_html) > 0:
                new_links = self.get_links(url_to_crawl, parsed_html)
                self.crawl_list += new_links

    def total_pages(self):
        return len(self.visited)

    def start(self):
        self.crawl(self.starting_url)
