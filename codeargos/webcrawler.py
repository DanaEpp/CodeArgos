#!/usr/bin/env python3
import requests
import re
from urllib.parse import urlparse
from tld import get_tld

class WebCrawler(object):
    def __init__(self, starting_url):
        self.starting_url = starting_url
        self.root_domain = self.extract_root_domain(starting_url)
        self.visited = set()

    def extract_root_domain(self, url):
        res = get_tld(url, as_object=True) 
        return "//" + res.fld

    def get_page(self, url):
        try:
            page = requests.get(url, headers={"User-Agent":"Mozilla/5.0 (CodeArgos)"}, timeout=5)                                
        except Exception as ex:
            print(ex)
            return ""
        return page.content.decode('latin-1')

    def get_links(self, url):    
        page = self.get_page(url)    
        parsed = urlparse(url)    
        base = f"{parsed.scheme}://{parsed.netloc}"    
        links = re.findall('''<a\s+(?:[^>]*?\s+)?href="([^"]*)"''', page)

        # Remove any links that are NOT part of the root domain we are crawling (keep it on target)
        links = [url for url in links if url.startswith(self.starting_url)]
        
        for i, link in enumerate(links):    
            if not urlparse(link).netloc:    
                link_with_base = base + link    
                links[i] = link_with_base       

        return set(filter(lambda x: 'mailto' not in x, links))    

    def extract_info(self, url):                                
        page = self.get_page(url)
        meta = re.findall("<meta .*?name=[\"'](.*?)['\"].*?content=[\"'](.*?)['\"].*?>", page)    
        return dict(meta)                                   

    def crawl(self, url):                   
        for link in self.get_links(url):    
            if link in self.visited:        
                continue                    
            self.visited.add(link)

            try:            
                info = self.extract_info(link)
                print(link)    
            except Exception as e:
                print( "Err on {0}: {1}".format(link, e) )
            
            self.crawl(link)    

    def start(self):
        self.crawl(self.starting_url)
