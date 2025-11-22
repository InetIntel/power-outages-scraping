from utils import BaseScraper
import os
import requests 
from datetime import datetime, timedelta
from utils import print_all_files_recursive

class Scraper(BaseScraper):
    # provide some sort of URL. this doesn't need to be exact URL you scrape (it can be dynamic),
    # but just have this here for documentation purposes
    url = ""

    # This dir_path is very important. files will be created/uploaded/processed
    # according to this dir_path. The file will be placed in raw/dir_path for raw
    # files or processed/dir_path for processed files.
    dir_path = ""

    def scrape(self):
        # TODO: implement
        pass

    def process(self):
        files_processed = 0

        # TODO: implement
        
        if files_processed == 0:
            raise RuntimeError(f"[process] nothing processed")