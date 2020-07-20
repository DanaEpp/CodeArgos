import sys
import sqlite3
from codeargos.scrapedpage import ScrapedPage
import threading
from os.path import isfile, getsize
import logging
import json

class DataStore:
    def __init__(self, db_file_name):
        # To handle the fact python doesn't like recursive cursors
        # for sqlite, we have to use thread locking to prevent mangling
        self.lock = threading.Lock()

        # sqlite3 does not like multithreading in python. 
        # We have to remove the thread id check.
        self.conn = sqlite3.connect( db_file_name, check_same_thread=False )
        self.conn.row_factory = sqlite3.Row

        self.db = self.conn.cursor()
        self.create_datastore()

    def close(self):
        self.db.close()
        self.conn.close()
    
    def create_datastore(self):
        try:
            self.lock.acquire(True)
            self.db.execute( 
                """CREATE TABLE IF NOT EXISTS 
                    pages (
                        url TEXT NOT NULL PRIMARY KEY, 
                        sig TXT NOT NULL, 
                        content TXT,
                        last_update DATETIME DEFAULT CURRENT_TIMESTAMP)
                """ )
            self.conn.commit()
        finally:
            self.lock.release()                

    def add_page(self, page):
        # As sqlite doesn't have UPSERT, this will do the trick
        try:
            self.lock.acquire(True)
            self.db.execute(
                """INSERT INTO pages VALUES( :url, :sig, :content, CURRENT_TIMESTAMP )
                    ON CONFLICT(url) 
                        DO UPDATE SET sig=:sig, content=:content, last_update=CURRENT_TIMESTAMP
                """, 
                { 
                    'url': page.url, 
                    'sig': page.signature, 
                    'content': page.content
                })
            self.conn.commit()
        finally:
            self.lock.release()
            
    def get_page(self, url):
        page = None
        try:
            self.lock.acquire(True)
            self.db.execute("SELECT * FROM pages WHERE url=:u", {'u': url})
            data = self.db.fetchone()
            if data:
                page = ScrapedPage( 
                    data['url'], 
                    data['sig'], 
                    data['content'])
        finally:
            self.lock.release()
        return page

    def dump_pages(self):
        try:
            self.lock.acquire(True)
            self.db.execute( "SELECT * FROM pages")
            pages = self.db.fetchall()
        finally:
            self.lock.release()

        for page in pages:
            print(page)