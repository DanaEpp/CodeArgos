#!/usr/bin/env python3

import os.path
import sys
import logging
from codeargos.datastore import DataStore
from codeargos.diff import Diff
from colorama import Fore, Back, Style, init

class DisplayDiff:
    def __init__(self, db_file_name):       
        try:
            if os.path.isfile(db_file_name):
                self.data_store = DataStore(db_file_name)
            else:
                msg = "Unable to find db file to read diff data. Aborting."
                logging.debug(msg)
                print(msg)
                sys.exit()
        except Exception as e:
            logging.exception(e)
            print("Exception thrown while trying to load the db file to read diff data. Aborting.")
            sys.exit()

    def show(self, diff_id):
        try:
            diff = self.data_store.get_diff(diff_id)

            if diff:

                print("\n[DIFF #{0}] {1} (Detected: {2}) ".format(diff.id, diff.url, diff.date) )
                lines = diff.content.split('\n')
                for line in lines:
                    if line.startswith('+'):
                        print( Fore.GREEN + line + Fore.RESET )
                    elif line.startswith('-'):
                        print( Fore.RED + line + Fore.RESET )
                    elif line.startswith('^'):
                        print( Fore.BLUE + line + Fore.RESET )
                    else:
                        print( line )
            else:
                print( "No diff by that id exists!")
        except Exception as e:
            logging.exception(e)
        