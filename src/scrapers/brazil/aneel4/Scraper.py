from utils import BaseScraper
import os
import requests 
from datetime import datetime, timedelta
from utils import print_all_files_recursive

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
            with open(f"./raw/{self.dir_path}/{self.year}_{date}-brazil-aneel-raw.html", "w") as f:
                f.write(res.text)

        print(f"Download for {self.year} data is complete")


    def process(self):
        print("inside process")
        files_processed = 0
        print_all_files_recursive(f"./raw/{self.dir_path.lstrip('./')}")

        for root, _, files in os.walk("./raw/{self.dir_path.lstrip('./')}"):
            for filename in files:
                local_path = os.path.join(root, filename)
                print(f"reading for processing: {local_path}")
                processed_file_path = local_path.replace("raw", "processed")
                print(processed_file_path)
                
                # NOTE: this example func doesn't do anything. it just writes the same thing back
                # TODO: make this do something
                with open(local_path, 'r') as source_file, \
                    open(processed_file_path, 'w') as destination_file:
                    for line in source_file:
                        destination_file.write(line)
                print(f"Successfully copied {local_path} to {processed_file_path}")
                files_processed += 1
        
        if files_processed == 0:
            raise RuntimeError(f"[process] nothing processed")