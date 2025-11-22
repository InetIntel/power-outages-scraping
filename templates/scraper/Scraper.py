from utils import BaseScraper
import os
import requests 
from datetime import datetime, timedelta
from utils import print_all_files_recursive

class Scraper(BaseScraper):
    # provide some sort of URL. this doesn't need to be exact URL you scrape (it can be dynamic),
    # but just have this here for documentation purposes
    url = ""

    """
    This dir_path is very important. Files will be created/uploaded/processed
    according to this dir_path to minio/s3 as well. 
    
    The file will be placed in ./raw/dir_path for raw files or ./processed/dir_path 
    for processed files.

    Structure dir_path as follows: `./your_country/your_power_company/.../...
    """
    dir_path = ""

    def scrape(self):
        # TODO: implement. make the API call, start selenium, etc.
        # NOTE: make sure to write the file to ./raw/self.dir_path
        # e.g.: ./raw/{self.dir_path}/{self.year}_{date}-brazil-aneel-raw.html"

        pass

    def process(self):
        files_processed = 0

        for root, _, files in os.walk(f"./raw/{self.dir_path.lstrip('./')}"):
            for filename in files:
                local_path = os.path.join(root, filename)
                processed_file_path = local_path.replace("raw", "processed")
                
                with open(processed_file_path, 'w') as destination_file:
                    # TODO: implement. feel free to edit anything, as long as you
                    # write to ./processed/self.dir_path
                    pass

                print(f"Successfully copied {local_path} to {processed_file_path}")

                files_processed += 1
        
        if files_processed == 0:
            raise RuntimeError(f"[process] nothing processed")