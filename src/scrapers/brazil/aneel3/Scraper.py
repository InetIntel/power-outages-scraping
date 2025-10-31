from utils import BaseScraper
import os
import requests 
from datetime import datetime

class Scraper(BaseScraper):
    year = 2025
    url = "https://www.youtube.com/"
    dir_path = f"./brazil/aneel"

    def scrape(self):
        print(f"Downloading {self.year} data")

        res = requests.get(self.url)
        res.raise_for_status()

        date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        with requests.get(self.url) as res:
            res.raise_for_status()
            with open(f"./raw/{self.dir_path}/{self.year}_{date}.html", "w") as f:
                f.write(res.text)

        print(f"Download for {self.year} data is complete")


    def upload_raw(self):
        print(f"[upload_raw] init")

        something_uploaded = False
        s3_path = ""
        for root, _, files in os.walk(f"./raw/{self.dir_path[2:]}"):
            for filename in files:
                local_path = os.path.join(root, filename)
                print(f"[upload_raw] reading {local_path}")
                s3_path = local_path.replace("\\", "/") # convert windows slashes
                s3_path = s3_path.replace("./", "") # remove leading `./`
                s3_path = s3_path.replace("raw/", "")
                print(f"Trying to upload from {local_path} to {s3_path}")
                self.storage_client.upload_file_raw(local_path, s3_path)
                something_uploaded = True
    
        if not something_uploaded:
            raise RuntimeError(f"[upload_raw] nothing uploaded")


    def process(self):
        for root, _, files in os.walk(f"./raw/{self.dir_path[2:]}"):
            for filename in files:
                local_path = os.path.join(root, filename)
                print(f"reading for processing: {local_path}")
                processed_file_path = local_path.replace("raw", "processed")
                
                with open(local_path, 'r') as source_file, \
                    open(processed_file_path, 'w') as destination_file:
                    for line in source_file:
                        destination_file.write(line)
                print(f"Successfully copied {local_path} to {processed_file_path}")