from utils import BaseScraper
import os
import requests 
from datetime import datetime, timedelta
from utils import print_all_files_recursive

class Scraper(BaseScraper):
    url = ""
    dir_path = ""

    def scrape(self):
        pass

    def process(self):
        files_processed = 0

        # TODO: implement
        
        if files_processed == 0:
            raise RuntimeError(f"[process] nothing processed")