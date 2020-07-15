import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlparse,urljoin
from bs4 import BeautifulSoup
from pprint import pprint
import logging

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
