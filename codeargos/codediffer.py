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
        diff_data = ""

        # Prep the two code blocks, after expanding into readable segments
        options = {
            "keep_function_indentation": True,
            "keep_array_indentation": True,
            "jslint_happy": True
            # "html": {
            #     "end_with_newline": True,
            #     "js": {
            #         "indent_size": 2
            #     },
            #     "css": {
            #         "indent_size": 2
            #     }
            # },
            # "css": {
            #     "indent_size": 1
            # },
            # "js": {
            #     "preserve_newlines": True
            # }
        }

        beautiful_old_code = jsbeautifier.beautify(original_code, options).splitlines()
        beautiful_new_code = jsbeautifier.beautify(new_code, options).splitlines()      

        if self.console_mode:
            diff = difflib.unified_diff(
                beautiful_old_code, beautiful_new_code,
                fromfile="before", tofile="after",
                lineterm="")

            color_diff = self.__color_diff(diff)
            print( "[CHANGED FILE] {0}".format(url))
            print('\n'.join(color_diff))
            diff_data = '\n'.join(diff)
            return diff_data
        else:
            # Generate an HTML diff file
            differ = difflib.HtmlDiff()
            diff_data = differ.make_file( beautiful_old_code, beautiful_new_code )
            return diff_data
        
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

