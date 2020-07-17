class ScriptBlock:
    def __init__(self, url, block, sig):
        self.page_url = url
        self.script_block = block
        self.script_sig = sig                

    @property
    def url(self):
        return self.page_url

    @property
    def script(self):
        return self.script_block

    @property
    def signature(self):
        return self.script_sig

    def __repr__(self):
        return "{ url:\"{0}\", code:\"{1}\", sig: \"{2}\" }".format(self.page_url, self.script_block, self.script_sig)
    
    def __str__(self):
        return "ScriptBlock('{0}', '{1}', '{2}')".format(self.page_url, self.script_block, self.script_sig) 

    