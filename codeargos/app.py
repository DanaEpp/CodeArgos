#!/usr/bin/env python3

import os
import sys
import getopt
import re
from codeargos.__version__ import __version__
import codeargos.Constants as Constants
from codeargos.enums import CodeArgosMode, CodeArgosPrintMode
from codeargos.webcrawler import WebCrawler
from codeargos.displaydiff import DisplayDiff
from datetime import tzinfo, timedelta, datetime, timezone
import logging

class CodeArgos:

    def __init__(self):
        self.visited = set()

    @classmethod
    def print_banner(cls):
        print("\n{0}===========================================".format(Constants.CYAN))
        print(" {0}CodeArgos{1} ({0}v{2}{1}) - Developed by @danaepp".format(Constants.WHITE, Constants.CYAN, __version__))
        print(" https://github.com/danaepp/CodeArgos")
        print("==========================================={0} \n".format(Constants.WHITE))

    @classmethod
    def display_usage(cls):
        print( ' RECON: codeargos.py -u example.com\n\t[-t thread_cnt] [-d] [-s] [-f /path/to/your.db]\n\t[-w generic|slack|teams|discord --wurl=https://hook.slack.com/some/webhook]\n\t[-p diff|id|both|none]' )       
        print( 'REVIEW: codeargos.py --diff 123 -f /path/to/your.db' )       
        print('\n')

    @classmethod
    def setup_logging(cls, log_level):
        if log_level is None:
            logging.basicConfig( 
                stream=sys.stdout, 
                level=log_level,
                format='%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%m/%d/%Y %I:%M:%S %p' )
        else:
            logging.basicConfig( 
                filename="codeargos.log", 
                level=log_level,
                format='%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%m/%d/%Y %I:%M:%S %p' )

    @classmethod
    def get_print_mode(cls,pmode):
        if pmode == "none":
            print_mode = CodeArgosPrintMode.NONE
        elif pmode == "id":
            print_mode = CodeArgosPrintMode.ID
        elif pmode == "diff":
            print_mode = CodeArgosPrintMode.DIFF
        else:
            print_mode = CodeArgosPrintMode.BOTH

        return print_mode

    @classmethod
    def get_scoped_targets(cls,file_path):
        scope = []
        try:
            scope_file = open( file_path, 'r')
            targets = scope_file.readlines()
            scope_file.close()
            for target in targets:
                scope.append(target.strip())
        except FileNotFoundError:
            print( "A valid scope target list file not be found.")
        except Exception as e:
            logging.exception(e)
        return scope

    @staticmethod
    def run(argv):
        CodeArgos.print_banner()

        diff_id = 0
        print_mode = CodeArgosPrintMode.BOTH
        targets = []
        seed_url = ""

        try:
            opts, args = getopt.getopt( argv, 
                "hu:t:ds:f:w:p:", 
                ["help", "url=", "threads=", "debug", "stats", "file", "webhook=", "wurl=", "webhookurl=", "diff=", "print=", "scope="])
        except getopt.GetoptError as err:
            logging.exception(err)
            logging.debug("opts: {0} | args: {1}".format(opts, args))
            CodeArgos.display_usage()
            sys.exit(2)

        threads = os.cpu_count() * 5
        log_level = None
        show_stats = False
        db_file_path = ""
        webhook_type = ""
        webhook_url = ""

        for opt, arg in opts:
            if opt in ( "-h", "--help"):
                CodeArgos.display_usage()
                sys.exit()
            elif opt in ( "-u", "--url"):
                seed_url = arg
            elif opt in ( "-t", "--threads"):
                try:
                    threads = int(arg, base=10)
                except ValueError:
                    print( "Invalid thread count. Using defaults")                    
                    threads = os.cpu_count() * 5
            elif opt in ( "-d", "--debug" ):
                log_level = logging.DEBUG
            elif opt in ( "--stats" ):
                show_stats = True
            elif opt in ( "-f", "--file" ):
                db_file_path = arg
            elif opt in ( "-w", "--webhook" ):
                webhook_type = arg.lower()
            elif opt in ( "--wurl", "--webhookurl" ):
                webhook_url = arg
            elif opt in ("--diff"):
                try:
                    diff_id = int(arg)
                except Exception as e:
                    logging.exception(e)   
            elif opt in ("-p", "--print"):
                print_mode = CodeArgos.get_print_mode(arg.lower())
            elif opt in ("-s", "--scope"):
                targets = CodeArgos.get_scoped_targets(arg)
                
        CodeArgos.setup_logging(log_level)

        if diff_id > 0 and db_file_path:
            diff_viewer = DisplayDiff(db_file_path)
            diff_viewer.show(diff_id)            
        else:
            if seed_url:
                scan_start = datetime.now(timezone.utc)
                print( "Attempting to scan {0} across {1} threads...".format(seed_url, threads))
                print( "Starting scan at {0} UTC".format(scan_start.strftime("%Y-%m-%d %H:%M")) )
                
                crawler = WebCrawler(seed_url, threads, show_stats, db_file_path, webhook_type, webhook_url, print_mode)
                crawler.start(targets)

                scan_end = datetime.now(timezone.utc)
                elapsed_time = scan_end - scan_start
                
                print( "Scan complete: reviewed {0} pages in {1}.".format( crawler.processed, elapsed_time ) )
            else:
                print( "Missing target (-u) parameter. Aborting!")
                CodeArgos.display_usage()


        