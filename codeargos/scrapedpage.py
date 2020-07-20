class ScrapedPage:
    def __init__(self, url, sig, content):
        self.page_url = url
        self.page_sig = sig
        self.page_content = content                

    @property
    def url(self):
        return self.page_url

    @property
    def signature(self):
        return self.page_sig

    @property
    def content(self):
        return self.page_content

    def __repr__(self):
        return "{ url:\"{0}\", sig: \"{1}\" }".format(self.page_url, self.page_sig)
    
    def __str__(self):
        return "Page('{0}', '{1}')".format(self.page_url, self.page_sig) 

    