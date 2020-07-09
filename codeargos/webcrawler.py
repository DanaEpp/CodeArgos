#!/usr/bin/env python3
import requests
import re
from urllib.parse import urlparse
from tld import get_tld
from bs4 import BeautifulSoup
from pprint import pprint

class WebCrawler(object):
    def __init__(self, starting_url):
        self.starting_url = starting_url
        self.root_domain = self.extract_root_domain(starting_url)
        self.visited = set()

    def extract_root_domain(self, url):
        res = get_tld(url, as_object=True) 
        return res.fld

    def get_page(self, url):

        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
            'User-Agent': 'Mozilla/5.0 (CodeArgos)'
        }

        try:
            page = requests.get(url, headers, timeout=5)
            parsed_html = BeautifulSoup(page.content, features='html.parser')
        except Exception as ex:
            print(ex)
            return ""
        return parsed_html

    def get_links(self, parsed_html):

        anchor_tags = parsed_html.find_all("a", href=True)

        links = []
        for i, tag in enumerate(anchor_tags):
            link = tag['href']
            if link.startswith(self.starting_url) and not link in links:
                links.append( link )

        return links    

    def crawl(self, url):
        parsed_html = self.get_page(url)

        for link in self.get_links(parsed_html):    
            if link in self.visited:        
                continue                    
            self.visited.add(link)
            print(url)
            self.crawl(link)    

    def start(self):
        self.crawl(self.starting_url)
