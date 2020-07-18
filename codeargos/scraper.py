import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlparse,urljoin
from bs4 import BeautifulSoup
from pprint import pprint
import hashlib
from codeargos.scriptblock import ScriptBlock, ScriptBlockType
from codeargos.scrapedpage import ScrapedPage

class Scraper:

    allowed_content = (
        'text/plain', 
        'text/html', 
        'text/javascript', 
        'application/x-httpd-php',
        'application/xhtml+xml'
        )

    def __init__(self, url, scraped_page):
        self.url = url
        self.old_scraped_page = scraped_page 
        self.internal_urls = None
        self.script_blocks = None

    def get_page(self, session, url):
        parsed_html = ""
        page_sig = None
        
        try:
            head = session.head(url)
            if head.status_code == 200:
                content_type = head.headers.get('Content-Type')
                if content_type.startswith(self.allowed_content):
                    response = session.get(url)
                    if response.ok: 
                        parsed_html = BeautifulSoup(response.content, features='html.parser')
                        page_sig = hashlib.sha256(response.text.encode('utf-8')).hexdigest()

        except Exception as ex:
            logging.exception(ex)
        
        return parsed_html, page_sig

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

    def get_script_blocks(self, parsed_html):

        script_blocks = []

        for code in parsed_html.find_all("script"):
            # TODO: Future enhancement - We currently do not extract inline script blocks, 
            # and we should. ie: onerror=alert(1)
            block_type = ScriptBlockType.BLOCK

            code_block = ""
            code_sig = ""

            if 'src' in code.attrs:
                block_type = ScriptBlockType.EXTERNAL
                # Since the actual code is external we have to fetch that first 
                code_src = code['src']
                parsed_url = urlparse(code_src)

                # In case we have relative path javascript files
                if not parsed_url.netloc:
                    code_src = urljoin(self.url, code_src)

                logging.debug( "Fetching external script at {0}".format(code_src))

                try:
                    response = requests.get(code_src)
                    if response.status_code == 200:
                        code_block = response.text
                except Exception as e:
                    logging.exception(e)
                    # If we couldn't fetch the code block we have to consider it dead and move on
                    continue
            else:
                # You would think .text would be the right place for block scripts, but you would be
                # wrong. Ends up it parks it in .string
                code_block = code.string

            if code_block:
                try:
                    code_sig = hashlib.sha256(code_block.encode('utf-8')).hexdigest()
                except Exception as e:
                    logging.exception(e)
                    # If we blow up on the crypto, we have to consider it a bad signature and should remove it, 
                    # forcing a change delta check for researcher analysis
                    continue

            block = ScriptBlock(self.url, code_block, code_sig, block_type)            
            script_blocks.append( block )

        return script_blocks

    def scrape(self):
        parsed_html = ""
        new_page_sig = ""
        session = requests.session()

        # Add incrimental backoff retry logic some we aren't slamming servers
        retry_strategy = Retry(
            total=10,
            status_forcelist=[104, 429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        try:
            parsed_html, new_page_sig = self.get_page(session, self.url)
        except Exception as e:
            logging.exception(e)

        # Check signature to see if the page has changed 
        # and if we even have to process the content further
        new_content = True
        if self.old_scraped_page is not None: 
            if self.old_scraped_page.signature == new_page_sig:                
                new_content = False
                logging.debug( "No changes detected on {0}".format(self.url))
        
        scraped_urls = []    
        if len(parsed_html) > 0:
            try:
                scraped_urls = self.get_links(self.url, parsed_html)
            except Exception as e:
                logging.exception(e)

        # We only need to fetch new script blocks if the page actually changed
        if new_content:
            # Grab any script blocks on the page
            try:
                self.script_blocks = self.get_script_blocks(parsed_html)
            except Exception as e:
                logging.exception(e)

        session.close()

        self.internal_urls = set(scraped_urls)
        
        return self.internal_urls, self.url, new_page_sig, self.script_blocks, new_content
