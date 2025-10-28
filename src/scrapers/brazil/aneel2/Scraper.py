import traceback
import sys

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
        self.year = year if year != None else datetime.now().year
        # self.url = "https://dadosabertos.aneel.gov.br/dataset/interrupcoes-de-energia-eletrica-nas-redes-de-distribuicao"
        self.url = "https://www.youtube.com/"
        self.dir_path = f"./aneel/{self.year}" # the dir to store all scraped files/data in

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

    def __get_page_data(self):
        """
        Dummy method that just extracts the raw HTML of the page. 
        """
        with requests.get(self.url, stream=True) as res:
                res.raise_for_status()
                with open(f"{self.dir_path}/random-data", "w") as f:
                    f.write(res.text)

    def scrape(self):
        print(f"Downloading {self.year} data", file=sys.stderr) 

        try:
            res = requests.get(self.url)
            res.raise_for_status()

            self.__create_dir()
            self.__get_page_data()

            # TODO: upload to minio and somehow let next contianer know where the file went


            print(f"Download for {self.year} data is complete", file=sys.stderr) 
            print(f"Starting raw upload", file=sys.stderr) 
            self.upload_raw()

        except Exception as e:
            print(f"An error occurred: {e}", file=sys.stderr) 
            traceback.print_exc() 
            sys.exit(1)

            

    def upload_raw(self):
        s3_path = ""
        for root, _, files in os.walk(self.dir_path):
            for filename in files:
                local_path = os.path.join(root, filename)
                s3_path = local_path.replace("\\", "/") # convert windows slashes
                s3_path = s3_path.replace("./", "") # remove leading `./`
                print(f"Trying to upload from {local_path} to {s3_path}", file=sys.stderr) 
                self.storage_client.upload_file_raw(local_path, s3_path)
        
        # Print the s3 key for the next step to access
        os.remove(local_path)
        
        # Return the FULL S3 Key for DAGU to capture
        full_s3_key = f"raw/{s3_path}"
        # return full_s3_key
        # return json.dumps({
        #     "s3_path": full_s3_key # TODO: what if we have multiple files?
        # })

        print("TEH FUCK", file=sys.stderr)


        print(json.dumps({
            "s3_path": full_s3_key
        }))

    def process(self, s3_dir):
        """
        Code to process (validate the files, check for types, NULL values, etc.) goes here
        """
        # Process each file in the given directory
        files_str_arr = self.storage_client.list_keys_by_prefix(s3_dir)
        for file_str in files_str_arr:
            # Make a new path: replace "raw" with "processed"; rest should be the same
            DIR_SPLIT = file_str.split("/")
            DIR_SPLIT[0] = "processed"
            file_str_new = "/".join(DIR_SPLIT)
            print(f"reading {file_str}")
            try:
                raw_content = self.storage_client.read_object(s3_path=file_str)
                
                # TODO: Processing logic here
                
                # Save the processed result back to the 'processed' location
                self.storage_client.upload_file_processed(
                    local_path=self.dir_path, 
                    s3_path= file_str_new
                )
            except Exception as e:
                print(f"Error during processing: {e}", file=sys.stderr) 


    def upload_processed(self):
        for root, _, files in os.walk(self.dir_path):
            for filename in files:
                local_path = os.path.join(root, filename)
                s3_path = local_path.replace("\\", "/") # convert windows slashes
                s3_path = s3_path.replace("./", "") # remove leading `./`
                self.storage_client.upload_file_processed(local_path, s3_path)

        print("Folder uploaded", file=sys.stderr) 