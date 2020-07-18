class ScrapedPage:
    def __init__(self, url, sig, script_blocks):
        self.page_url = url
        self.page_sig = sig
        self.script_blocks = script_blocks                

    @property
    def url(self):
        return self.page_url

    @property
    def signature(self):
        return self.page_sig

    @property
    def scripts(self):
        return self.script_blocks

    def __repr__(self):
        return "{ url:\"{0}\", sig: \"{1}\" }".format(self.page_url, self.page_sig)
    
    def __str__(self):
        return "Page('{0}', '{1}')".format(self.page_url, self.page_sig) 

    