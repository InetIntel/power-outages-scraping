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
        # os.makedirs(self.dir_path, exist_ok=True)
        dir_without_first_slash = self.dir_path[2:]
        os.makedirs(f"./raw/{dir_without_first_slash}", exist_ok=True)
        os.makedirs(f"./processed/{dir_without_first_slash}", exist_ok=True)

    def __get_page_data(self):
        """
        Dummy method that just extracts the raw HTML of the page. 
        """
        with requests.get(self.url, stream=True) as res:
            res.raise_for_status()
            with open(f"./raw/{self.dir_path}/random-data.html", "w") as f:
                f.write(res.text)

    def scrape(self):
        print(f"Downloading {self.year} data", file=sys.stderr) 

        try:
            res = requests.get(self.url)
            res.raise_for_status()

            self.__create_dir()
            self.__get_page_data()

            print(f"Download for {self.year} data is complete", file=sys.stderr) 
            print(f"Starting raw upload", file=sys.stderr) 
            # self.upload_raw()

        except Exception as e:
            print(f"An error occurred: {e}", file=sys.stderr) 
            traceback.print_exc() 
            sys.exit(1)
            

    def upload_raw(self):
        s3_path = ""
        for root, _, files in os.walk(f"./raw/{self.dir_path}"):
            for filename in files:
                local_path = os.path.join(root, filename)
                s3_path = local_path.replace("\\", "/") # convert windows slashes
                s3_path = s3_path.replace("./", "") # remove leading `./`
                print(f"Trying to upload from {local_path} to {s3_path}", file=sys.stderr) 
                self.storage_client.upload_file_raw(local_path, s3_path)


    def process(self):
        for root, _, files in os.walk(f"./raw/{self.dir_path}"):
            for raw_file_path in files:
                print(f"reading for processing: {raw_file_path}")
                processed_file_path = f"./processed/{self.dir_path}"

                try:
                    with open(raw_file_path, 'r') as source_file, \
                        open(processed_file_path, 'w') as destination_file:
                        for line in source_file:
                            destination_file.write(line)
                    print(f"Successfully copied {raw_file_path} to {processed_file_path}")
                except Exception as e:
                    print(f"An error occurred file copy: {e}")


    def upload_processed(self):
        for root, _, files in os.walk(f"./processed/{self.dir_path}"):
            for filename in files:
                local_path = os.path.join(root, filename)
                s3_path = local_path.replace("\\", "/") # convert windows slashes
                s3_path = s3_path.replace("./", "") # remove leading `./`
                self.storage_client.upload_file_processed(local_path, s3_path)

        print("Folder uploaded", file=sys.stderr) 