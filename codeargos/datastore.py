import sqlite3
from codeargos.scrapedpage import ScrapedPage

class DataStore:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(':memory:') 
        # self.conn = sqlite3.connect( db_name + '.db')
        self.db = self.conn.cursor()
        self.create_datastore()

    def close(self):
        self.conn.close()
    
    def create_datastore(self):
        with self.conn:
            self.db.execute( "CREATE TABLE pages (url TEXT, sig TXT)" )

    def insert_page(self, page):
        with self.conn:
            self.db.execute("INSERT INTO pages VALUE( :url, :sig )", {'url': page.url, 'sig': page.signature} )

    def get_page(self, url):
        with self.conn:
            self.db.execute("SELECT * FROM pages WHERE url=:u", {'u': url})
            return self.db.fetchone()