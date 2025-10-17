import boto3
from botocore.client import Config
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from utils import Uploader

class Aneel:
    def __init__(self, year=None):
        print("initting")
        self.uploader = Uploader("brazil")
        self.year = datetime.now().year
        if year:
            self.year = year
        self.url = "https://dadosabertos.aneel.gov.br/dataset/interrupcoes-de-energia-eletrica-nas-redes-de-distribuicao"
        self.dir_path = f"./aneel/raw/{self.year}" # the dir to store all scraped files/data in
        self.raw_data_path = None # to be replaced by upload client later

    def __create_dir(self):
        os.makedirs(self.dir_path, exist_ok=True)

    def __get_filename_from_url(self, url):
        _, _, tail = url.partition("/download/")
        return tail

    def __get_a_tags_from_html_page(self, html_page):
        result = {}
        soup = BeautifulSoup(html_page, "html.parser")
        a_tags = soup.find_all("a", "resource-url-analytics")
        for tag in a_tags:
            url = tag.get("href")
            filename = self.__get_filename_from_url(url)
            if ".csv" in url and str(self.year) in filename:
                result[filename] = url

        return result

    def __download_csv(self, filename_and_url):
        for filename, url in filename_and_url.items():
            print("downloading csv")
            with requests.get(url, stream=True) as res:
                res.raise_for_status()
                with open(f"{self.dir_path}/{filename}", "wb") as f:
                    for chunk in res.iter_content(chunk_size=2**12):
                        if chunk:
                            f.write(chunk)

    def __download_csv_with_progress_bar(self, filename_and_url):
        for filename, url in filename_and_url.items():
            with requests.get(url, stream=True) as res:
                res.raise_for_status()
                total_size = int(res.headers.get("content-length", 0))
                with (
                    open(f"{self.dir_path}/{filename}", "wb") as f,
                    tqdm(
                        total=total_size,
                        unit="B",
                        unit_scale=True,
                        desc=f"Downloading {self.year}",
                    ) as bar,
                ):
                    for chunk in res.iter_content(chunk_size=2**12):
                        if chunk:
                            f.write(chunk)
                            bar.update(len(chunk))

    def scrape(self):
        print("?????????????????????????")
        print(f"Downloading {self.year} data", flush=True)

        res = requests.get(self.url)
        res.raise_for_status()

        filename_and_url = self.__get_a_tags_from_html_page(res.text)

        if len(filename_and_url) == 0:
            print(f"No data available for year {self.year}")
            return

        self.__create_dir()

        print("starting download", flush=True)
        if os.environ.get("ENV") == "local":
            self.__download_csv_with_progress_bar(filename_and_url)
        else:
            self.__download_csv(filename_and_url)

        print(f"Download for {self.year} data is complete")


    def process(self):
        """
        Code to process (validate the files, check for types, NULL values, etc.) goes here
        """
        # Inside post_process.py context
        # storage_client = self.uploader.read_object(self.)

        # 1. Define the S3 path for the file you want to process (it must exist in 'raw')
        YEAR = 2024
        FILENAME = "some_data.csv"
        RAW_S3_PATH = f"raw/{YEAR}/{FILENAME}" 

        # 2. Read the content directly into memory for processing (if small enough)
        try:
            raw_csv_content = storage_client.read_object(s3_path=RAW_S3_PATH)
            
            # --- Run your processing logic here on raw_csv_content ---
            # For example, reading it with pandas:
            # import pandas as pd
            # df = pd.read_csv(io.StringIO(raw_csv_content))
            # processed_df = df[df['some_column'] > 0]
            
            # 3. Save the processed result back to the 'processed' location
            PROCESSED_FILENAME = "cleaned_data.csv"
            # In a real scenario, you'd write the processed data to a *temporary* local path 
            # or stream it directly if your client supports streaming upload.
            # For simplicity, let's assume you wrote it to a temp local file named 'temp_processed.csv':
            # storage_client.upload_file_processed(
            #     local_path='temp_processed.csv', 
            #     s3_path=f"{YEAR}/{PROCESSED_FILENAME}" # Note: YEAR is prepended by upload_file_processed
            # )
            
        except Exception as e:
            print(f"Error during processing: {e}")


    def upload(self):
        for root, _, files in os.walk(self.dir_path):
            for filename in files:
                local_path = os.path.join(root, filename)
                s3_path = local_path.replace("\\", "/") # convert windows slashes
                s3_path = s3_path.replace("./", "") # remove leading `./`
                self.uploader.upload_file_processed(local_path, s3_path)

        print("Folder uploaded")