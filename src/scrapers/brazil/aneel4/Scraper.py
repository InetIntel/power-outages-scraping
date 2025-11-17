from utils import BaseScraper
import os
import requests 
from datetime import datetime, timedelta

class Scraper(BaseScraper):
    year = 2025
    url = "https://www.youtube.com/"
    dir_path = f"./brazil/aneel"
    """
    raw/country_name/power_company/date-scraping-for__date-scraping-on__raw-country-power_company
    processed
    """

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

        self.upload_raw()


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

    
    def download_raw_files(self, time_delta=None):
        # check for files made within the last 10 min by default
        if time_delta is None:
            time_delta = timedelta(minutes=10)

        time_start = datetime.now() - time_delta
        raw_files = self.get_raw_since_time(time_start, self.dir_path[2:])

        for file_name in raw_files:
            print(f"[download_raw_files] downloading {file_name}")
            self.download_raw(s3_path=file_name, local_path=f"./processed/{file_name}")


    def download_process_upload(self, time_delta=None):
        self.download_raw_files(time_delta)
        self.process()
        self.upload_processed()