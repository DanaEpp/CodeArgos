#!/usr/bin/env python3

import sys
import getopt
import re
from codeargos.__version__ import __version__
import codeargos.Constants as Constants
from datetime import tzinfo, timedelta, datetime, timezone

class CodeArgos:

    target_host=''

    @classmethod
    def print_banner(cls):
        print("\n{0}===========================================".format(Constants.CYAN))
        print(" {0}CodeArgos{1} ({0}v{2}{1}) - Developed by @danaepp".format(Constants.WHITE, Constants.CYAN, __version__))
        print(" https://github.com/danaepp/CodeArgos")
        print("==========================================={0} \n".format(Constants.WHITE))

    @classmethod
    def display_usage(cls):
        print( 'codeargos.py -u example.com' )       

    @staticmethod
    def run(argv):
        CodeArgos.print_banner()

        try:
            opts, args = getopt.getopt(argv, "hu:", ["help", "url="])
        except getopt.GetoptError:
            CodeArgos.display_usage()
            sys.exit(2)

        for opt, arg in opts:
            if opt in ( "-h", "--help"):
                CodeArgos.display_usage()
                sys.exit()
            elif opt in ( "-u", "--url"):
                CodeArgos.target_host = arg
                if( CodeArgos.target_host.startswith('http')):
                    CodeArgos.target_host = re.sub( r'https?://', '', CodeArgos.target_host, 1 )
        
        code_blocks = 0
        scan_start = datetime.now(timezone.utc)
        print( "Attempting to scan {0}".format(CodeArgos.target_host))
        print( "Starting scan at {0} UTC".format(scan_start.strftime("%Y-%m-%d %H:%M")) )

        scan_end = datetime.now(timezone.utc)
        elapsed_time = scan_end - scan_start
        print( "Scan complete: found {0} code file/blocks in {1}".format( code_blocks, elapsed_time ) )