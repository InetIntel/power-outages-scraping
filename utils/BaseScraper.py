from abc import ABC, abstractmethod
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from utils import StorageClient

class BaseScraper(ABC):
    def __init__(self):
        """
        Initializes the storage client, local directories, and place to scrape from.
        """
        is_docker = os.environ.get("IS_DOCKER_CONTAINER") == "true"
        if is_docker:
            self.storage_client = StorageClient()
        else:
            self.storage_client = None

        # make sure that child classes have a url and dir_path
        if not hasattr(self, 'url') or not self.url:
            raise NotImplementedError("Subclasses must define the 'url' attribute.")
        if not hasattr(self, 'dir_path') or not self.dir_path:
            raise NotImplementedError("Subclasses must define the 'dir_path' attribute (e.g., './brazil/aneel').")
            
        # create the local raw/ and processed/ directories for temporary storage.
        self.raw_local_dir = f"./raw/{self.dir_path.lstrip('./')}"
        self.processed_local_dir = f"./processed/{self.dir_path.lstrip('./')}"
        os.makedirs(self.raw_local_dir, exist_ok=True)
        os.makedirs(self.processed_local_dir, exist_ok=True)


    # ======================================================================
    # CONCRETE METHODS (Reusable Boilerplate Logic)
    # ======================================================================
    def __upload(self, is_raw: bool):
        """
        
        """
        something_uploaded = False
        parent_dir = "raw" if is_raw else "processed"
        local_dir = self.raw_local_dir if is_raw else self.processed_local_dir
        s3_path = ""
        for root, _, files in os.walk(local_dir):
            for filename in files:
                local_path = os.path.join(root, filename)
                print(f"[upload_{parent_dir}] reading {local_path}")
                s3_path = local_path.replace("\\", "/") # convert windows slashes
                s3_path = s3_path.replace("./", "") # remove leading `./`
                # s3 will have raw/processed as a bucket name, so remove it here
                s3_path = s3_path.replace(f"{parent_dir}/", "") 
                print(f"[upload_{parent_dir}] try upload from {local_path} to {s3_path}")
                if is_raw:
                    self.storage_client.upload_file_raw(local_path, s3_path)
                else:
                    self.storage_client.upload_file_processed(local_path, s3_path)
                something_uploaded = True
    
        if not something_uploaded:
            raise RuntimeError(f"[upload_{parent_dir}] nothing uploaded")
        
        
    def upload_raw(self) -> str:
        self.__upload(is_raw=True)
        

    def upload_processed(self):
        self.__upload(is_raw=False)


    def download_raw_files(self, time_delta: Optional[timedelta] = None):
        """
        Downloads all files from s3 that were made since `time_delta`.
        """
        # check for files made within the last N min by default
        if time_delta is None:
            time_delta = timedelta(minutes=10)

        time_start = datetime.now() - time_delta
        raw_files = self.get_raw_since_time(time_start, self.dir_path[2:])

        for file_name in raw_files:
            print(f"[download_raw_files] downloading {file_name}")
            self.storage_client.download_file(s3_path=file_name, local_path=f"./raw/{file_name}", is_raw=True)


    def get_raw_since_time(self, start_time, prefix):
        return self.storage_client.get_keys_since_time(prefix, start_time)
    

    # ======================================================================
    # ABSTRACT METHODS (MUST be implemented by the user)
    # ======================================================================
    @abstractmethod
    def scrape(self) -> None:
        """
        Scrape data, save locally to self.raw_local_dir.
        """
        pass
    

    @abstractmethod
    def process(self) -> None:
        """
        Process the local data and savei into self.processed_local_dir
        """
        pass


    def scrape_upload(self):
        self.scrape()
        self.upload_raw()


    def download_process_upload(self, time_delta=None):
        self.download_raw_files(time_delta)
        self.process()
        self.upload_processed()