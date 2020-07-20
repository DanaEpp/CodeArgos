#!/usr/bin/env python3

import difflib
import sys
from colorama import Fore, Back, Style, init
import pprint
import jsbeautifier

class CodeDiffer:
    def __init__(self, console_mode=True):
        self.console_mode = console_mode
        pass
    
    def diff(self, url, original_code, new_code):
        # Prep the two code blocks, after expanding into readable segments
        options = {
            "keep_function_indentation": 0,
            "indent_with_tabs": 1
        }

        beautiful_old_code = jsbeautifier.beautify(original_code, options).splitlines()
        beautiful_new_code = jsbeautifier.beautify(new_code, options).splitlines()      


        if self.console_mode:
            diff = difflib.unified_diff(
                beautiful_old_code, beautiful_new_code,
                fromfile="before", tofile="after",
                lineterm="")

            diff = self.__color_diff(diff)
            print( "[CHANGED FILE] {0}".format(url))
            print('\n'.join(diff))
        else:
            # Generate an HTML diff file
            differ = difflib.HtmlDiff()
            html = differ.make_file( beautiful_old_code, beautiful_new_code )
            return html
        
    def __color_diff(self, diff):
        for line in diff:
            if line.startswith('+'):
                yield Fore.GREEN + line + Fore.RESET
            elif line.startswith('-'):
                yield Fore.RED + line + Fore.RESET
            elif line.startswith('^'):
                yield Fore.BLUE + line + Fore.RESET
            else:
                yield line
