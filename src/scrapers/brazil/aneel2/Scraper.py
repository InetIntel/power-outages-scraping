import boto3
from botocore.client import Config
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from utils import StorageClient
import json

class Scraper:
    def __init__(self, year=None, storage_client=None):
        self.storage_client = StorageClient()
        self.year = year if year else datetime.now().year
        self.url = "https://dadosabertos.aneel.gov.br/dataset/interrupcoes-de-energia-eletrica-nas-redes-de-distribuicao"
        self.dir_path = f"./aneel/raw/{self.year}" # the dir to store all scraped files/data in

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
        print(f"Downloading {self.year} data", flush=True)

        res = requests.get(self.url)
        res.raise_for_status()

        filename_and_url = self.__get_a_tags_from_html_page(res.text)

        if len(filename_and_url) == 0:
            print(f"No data available for year {self.year}")
            return

        self.__create_dir()

        # if os.environ.get("ENV") == "local":
        #     self.__download_csv_with_progress_bar(filename_and_url)
        # else:
        self.__download_csv(filename_and_url)

        # TODO: upload to minio and somehow let next contianer know where the file went


        print(f"Download for {self.year} data is complete")


    def upload_raw(self):
        s3_path = ""
        for root, _, files in os.walk(self.dir_path):
            for filename in files:
                local_path = os.path.join(root, filename)
                s3_path = local_path.replace("\\", "/") # convert windows slashes
                s3_path = s3_path.replace("./", "") # remove leading `./`
                self.storage_client.upload_file_raw(local_path, s3_path)
        
        # Print the s3 key for the next step to access
        # TODO: have process use the local data, but still upload raw anyways
        # for the sake of posterity -- reduce S3 calls while being fast?
        os.remove(local_path)
        
        # Return the FULL S3 Key for DAGU to capture
        full_s3_key = f"raw/{s3_path}"
        # return full_s3_key
        return json.dumps({
            "s3_path": full_s3_key # what if we have multiple files?
        })


    def process(self, s3_dir):
        """
        Code to process (validate the files, check for types, NULL values, etc.) goes here
        """
        # Inside post_process.py context
        # storage_client = self.uploader.read_object(self.)


        # 2. Read the content directly into memory for processing (if small enough)
        files_str_arr = self.storage_client.list_keys_by_prefix(s3_dir)
        for file_str in files_str_arr:
            # Make a new path: replace "raw" with "processed"; rest should be the same
            DIR_SPLIT = file_str.split("/")
            DIR_SPLIT[0] = "processed"
            file_str_new = "/".join(DIR_SPLIT)

            try:
                raw_content = self.storage_client.read_object(s3_path=file_str)
                
                # --- Run your processing logic here on raw_csv_content ---
                
                # 3. Save the processed result back to the 'processed' location
                PROCESSED_FILENAME = ""
                self.storage_client.upload_file_processed(
                    local_path='', 
                    s3_path= file_str_new
                )
            except Exception as e:
                print(f"Error during processing: {e}")


    def upload_processed(self):
        for root, _, files in os.walk(self.dir_path):
            for filename in files:
                local_path = os.path.join(root, filename)
                s3_path = local_path.replace("\\", "/") # convert windows slashes
                s3_path = s3_path.replace("./", "") # remove leading `./`
                self.storage_client.upload_file_processed(local_path, s3_path)

        print("Folder uploaded")