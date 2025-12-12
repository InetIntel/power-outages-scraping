import boto3
from botocore.client import Config
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from utils import Uploader


class Aneel:
    def __init__(self, uploader, year=None):
        print("initting")
        self.uploader = uploader
        self.year = datetime.now().year
        if year:
            self.year = year
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
            print("downloading csv")
            with requests.get(url, stream=True) as res:
                res.raise_for_status()
                with open(f"{self.dir_path}/{filename}", "wb") as f:
                    for chunk in res.iter_content(chunk_size=2**12):
                        if chunk:
                            f.write(chunk)
            break # TODO: remove this -- it'll quit after just 1 file 

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

    def upload(self):
        for root, _, files in os.walk(self.dir_path):
            for filename in files:
                local_path = os.path.join(root, filename)
                s3_path = local_path.replace("\\", "/")
                s3_path = local_path.replace("./", "")
                self.uploader.upload_file(local_path, s3_path)

        print("✅ Folder uploaded")
        #

if __name__ == "__main__":
    print("in main", flush=True)
    s = Aneel(Uploader("brazil"))
    s.scrape()
    s.upload()
