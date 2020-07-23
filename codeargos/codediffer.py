#!/usr/bin/env python3

import difflib
import sys
from colorama import Fore, Back, Style, init
import pprint
import jsbeautifier
from enum import IntEnum
from itertools import tee

class CodeDifferMode(IntEnum):
    UNIFIED = 0
    HTML = 1

class CodeDiffer:
    def __init__(self, console=False, mode=CodeDifferMode.UNIFIED):
        self.console = console
        self.mode = mode
    
    def diff(self, url, original_code, new_code):
        diff_data = ""

        # Prep the two code blocks, after expanding into readable segments
        options = {
            "keep_function_indentation": True,
            "keep_array_indentation": True,
            "jslint_happy": True
        }

        beautiful_old_code = jsbeautifier.beautify(original_code, options).splitlines()
        beautiful_new_code = jsbeautifier.beautify(new_code, options).splitlines()      

        if self.mode == CodeDifferMode.UNIFIED:
            delta = difflib.unified_diff(
                beautiful_old_code, beautiful_new_code,
                fromfile="before : {0}".format(url), tofile="after : {0}".format(url),
                lineterm="")

            diff_data = '\n'.join(delta)
            
            return diff_data
        else:
            # Generate an HTML diff file
            differ = difflib.HtmlDiff()
            diff_data = differ.make_file( beautiful_old_code, beautiful_new_code )
            
            if self.console:
                print( "[CHANGED FILE] {0}".format(url))
                print(diff_data)

            return diff_data