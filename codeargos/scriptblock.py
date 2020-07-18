from enum import IntEnum
import json

class ScriptBlockType(IntEnum):
    BLOCK = 1
    INLINE = 2
    EXTERNAL = 3

class ScriptBlock(dict):
    def __init__(self, url, block, sig, block_type):
        self.page_url = url
        self.script_block = block
        self.script_sig = sig
        self.block_type = block_type                
        dict.__init__(self, url=url, script=block, sig=sig, block_type=block_type )

    @property
    def url(self):
        return self.page_url

    @property
    def script(self):
        return self.script_block

    @property
    def signature(self):
        return self.script_sig

    @property
    def script_type(self):
        return self.block_type

    def __repr__(self):
        return "{ url:\"{0}\", code:\"{1}\", sig: \"{2}\" }".format(self.page_url, self.script_block, self.script_sig)
    
    def __str__(self):
        return "ScriptBlock('{0}', '{1}', '{2}')".format(self.page_url, self.script_block, self.script_sig) 
