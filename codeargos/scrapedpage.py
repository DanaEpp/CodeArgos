import hashlib

class ScrapedPage:
    def __init__(self, url, content):
        self.url = url
        self.page_sig = hashlib.sha256(content).hexdigest()        

    @property
    def url(self):
        return self.url

    @property
    def signature(self):
        return self.page_sig

    def __repr__(self):
        return "{ url:\"{0}\", sig: \"{1}\" }".format(self.url, self.page_sig)
    
    def __str__(self):
        return "Page('{0}', '{1}')".format(self.url, self.page_sig) 

    