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
    def __init__(self, year=None):
        self.storage_client = StorageClient()
        self.year = year if year != None else datetime.now().year
        self.url = "https://www.youtube.com/"
        self.dir_path = f"./brazil/aneel" # the dir to store all scraped files/data in
        self.__create_dir()


    def __create_dir(self):
        # os.makedirs(self.dir_path, exist_ok=True)
        dir_without_first_slash = self.dir_path[2:]
        os.makedirs(f"./raw/{dir_without_first_slash}", exist_ok=True)
        os.makedirs(f"./processed/{dir_without_first_slash}", exist_ok=True)


    def __get_page_data(self):
        """
        Dummy method that just extracts the raw HTML of the page. 
        """
        date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        with requests.get(self.url) as res:
            res.raise_for_status()
            with open(f"./raw/{self.dir_path}/{self.year}_{date}.html", "w") as f:
                f.write(res.text)

        # print eveyrthing
        # def print_all_files_recursive(directory_path):
        #     """
        #     Prints the full path of all files within a given directory
        #     and its subdirectories.
        #     """
        #     for root, _, files in os.walk(directory_path):
        #         for file in files:
        #             full_file_path = os.path.join(root, file)
        #             print(full_file_path)

        # # Example usage:
        # # Replace '.' with the desired directory path if you want to scan a different location
        # print("printing dirs: ")
        # target_directory = '.'
        # print_all_files_recursive(target_directory)


    def scrape(self):
        print(f"Downloading {self.year} data")

        res = requests.get(self.url)
        res.raise_for_status()

        self.__get_page_data()

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


    def upload_processed(self):
        print(f"[upload_processed] init")

        something_uploaded = False
        s3_path = ""
        for root, _, files in os.walk(f"./processed/{self.dir_path[2:]}"):
            for filename in files:
                local_path = os.path.join(root, filename)
                print(f"[upload_processed] reading {local_path}")
                s3_path = local_path.replace("\\", "/") # convert windows slashes
                s3_path = s3_path.replace("./", "") # remove leading `./`
                s3_path = s3_path.replace("processed/", "")
                print(f"Trying to upload from {local_path} to {s3_path}")
                self.storage_client.upload_file_processed(local_path, s3_path)
                something_uploaded = True
        
        if not something_uploaded:
            raise RuntimeError(f"[upload_processed] nothing uploaded")