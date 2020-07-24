import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlparse,urljoin
from bs4 import BeautifulSoup
from pprint import pprint
import hashlib
from codeargos.scrapedpage import ScrapedPage
from codeargos.codediffer import CodeDiffer, CodeDifferMode

class Scraper:

    allowed_content = (
        'text/plain', 
        'text/html', 
        'application/x-httpd-php',
        'application/xhtml+xml',
        'application/javascript',
        'application/ecmascript',
        'application/x-ecmascript',
        'application/x-javascript',
        'text/javascript',
        'text/ecmascript',
        'text/javascript1.0',
        'text/javascript1.1',
        'text/javascript1.2',
        'text/javascript1.3',
        'text/javascript1.4',
        'text/javascript1.5',
        'text/jscript',
        'text/livescript',
        'text/x-ecmascript',
        'text/x-javascript'
        )

    def __init__(self, url, scraped_page):
        self.url = url
        self.old_scraped_page = scraped_page 
        self.internal_urls = None

    def get_page(self, session, url):
        response = None
        
        try:
            # This is fetching twice, but the first lets us determine if its a 
            # filetype we can actually process or not, which saves overall on 
            # bandwidth for files and images we just don't care about
            head = session.head(url)
            if head.status_code == 200:
                content_type = head.headers.get('Content-Type')
                if content_type.startswith(self.allowed_content):
                    response = session.get(url)
        except Exception as ex:
            logging.exception(ex)
        
        return response

    def get_links(self, url, parsed_html):

        links = []

        try:
            # Get links to other pages within the app
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

            # Get links to javascript files used by the app
            for script in parsed_html.find_all("script"):

                if 'src' in script.attrs:
                    script_url = script['src']
                    parsed_url = urlparse(script_url)

                    # In case we have relative path javascript files
                    if not parsed_url.netloc:
                        script_url = urljoin(self.url, script_url)
                    
                    links.append( script_url )
        except Exception as e:
            logging.exception(e)

        return links    

    def check_changes(self, new_sig, content):
        # Check signature to see if the page has changed 
        # and if we even have to process the content further
        new_content = True
        diff_content = ""
        if self.old_scraped_page: 
            if self.old_scraped_page.signature == new_sig:                
                new_content = False
            else:
                msg = "Changes detected on {0}".format(self.url)
                logging.debug(msg)
                differ = CodeDiffer(True, CodeDifferMode.UNIFIED)
                diff_content = differ.diff( self.url, self.old_scraped_page.content, content )

        return new_content, diff_content

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
            response = self.get_page(session, self.url)
            if response and response.ok: 
                raw_content = ""
                parsed_html = BeautifulSoup(response.content, features='html.parser')

                # We only want to hash the code blocks in the page, not the entire page, unless of course 
                # it's a Javascript file. Otherwise any HTML code change affects an change diff, when we really
                # only want to be alerted of Javascript changes
                if self.url.lower().endswith(".js"):
                    raw_content = response.text
                else:
                    # Fetch all the script blocks that are NOT references to external scripts
                    for script in parsed_html.find_all("script"):
                        if 'src' not in script.attrs:
                            # OK, its a local code block. Add it to what we have so we can hash all the blocks
                            # as one entity.
                            raw_content += script.string

                new_page_sig = hashlib.sha256(raw_content.encode('utf-8')).hexdigest() if raw_content else "NOSCRIPTS"
            else:
                status_code = response.status_code if response else "unknown"
                logging.debug( "Received error status {0} when fetching {1}".format(status_code, self.url))
        except Exception as e:
            logging.exception(e)

        new_content, diff_content = self.check_changes(new_page_sig, raw_content)
        
        scraped_urls = self.get_links(self.url, parsed_html)

        session.close()

        self.internal_urls = set(scraped_urls)
        
        return self.internal_urls, self.url, new_page_sig, new_content, raw_content, diff_content
