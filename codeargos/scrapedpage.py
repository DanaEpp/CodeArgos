class ScrapedPage:
    def __init__(self, url, sig, content):
        self.__page_url = url
        self.__page_sig = sig
        self.__page_content = content                

    @property
    def url(self):
        return self.__page_url

    @property
    def signature(self):
        return self.__page_sig

    @property
    def content(self):
        return self.__page_content

    def __repr__(self):
        return "{ url:\"{0}\", sig: \"{1}\" }".format(self.__page_url, self.__page_sig)
    
    def __str__(self):
        return "Page('{0}', '{1}')".format(self.__page_url, self.__page_sig) 

    