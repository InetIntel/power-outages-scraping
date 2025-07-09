import boto3
from botocore.client import Config
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


class Aneel:
    def __init__(self, year=None):
        self.year = datetime.now().year
        if year:
            self.year = year
        self.url = "https://dadosabertos.aneel.gov.br/dataset/interrupcoes-de-energia-eletrica-nas-redes-de-distribuicao"
        self.dir_path = f"./aneel/raw/{self.year}"

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
        print(f"Downloading {self.year} data")

        res = requests.get(self.url)
        res.raise_for_status()

        filename_and_url = self.__get_a_tags_from_html_page(res.text)

        if len(filename_and_url) == 0:
            print(f"No data available for year {self.year}")
            return

        self.__create_dir()

        if os.environ.get("ENV") == "local":
            self.__download_csv_with_progress_bar(filename_and_url)
        else:
            self.__download_csv(filename_and_url)

        print(f"Download for {self.year} data is complete")

    def upload(self):
        # Configure S3 client for MinIO
        s3 = boto3.client(
            "s3",
            endpoint_url="http://host.docker.internal:9000",  # Your MinIO server URL
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin",
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )

        # Create bucket (if it doesn't exist)
        bucket_name = "brazil"
        try:
            s3.create_bucket(Bucket=bucket_name)
        except s3.exceptions.BucketAlreadyOwnedByYou:
            pass

        # Walk through the folder and upload files
        for root, dirs, files in os.walk(self.dir_path):
            for filename in files:
                local_path = os.path.join(root, filename)
                # relative_path = os.path.relpath(local_path, self.dir_path)
                s3_path = local_path.replace("\\", "/")  # S3 uses forward slashes
                s3_path = local_path.replace("./", "")  # S3 uses forward slashes

                print(f"Uploading {local_path} to s3://{s3_path}")
                s3.upload_file(local_path, bucket_name, s3_path)

        print("✅ Folder uploaded")


if __name__ == "__main__":
    s = Aneel()
    s.scrape()
    s.upload()
