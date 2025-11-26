import json
import os
from bs4 import BeautifulSoup
from datetime import datetime
from utils.upload import Uploader


class Process_Ikeja:
    def __init__(self, year, month, today, file=None):
        self.year = year
        self.month = month
        self.today = today
        self.file = file
        self.bucket_name = "nigeria"
        try:
            self.uploader = Uploader(self.bucket_name)
            print("Initialized uploader.")
        except Exception as e:
            print(f"Error initializing uploader: {e}")
            self.uploader = None

    def download_raw_file(self, date=None):
        if date is None:
            date = self.today
        else:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            self.year = str(date_obj.year)
            self.month = str(date_obj.month).zfill(2)
            self.today = date

        file_name = f"power_outages.NG.ikeja.raw.{date}.html"
        s3_path = f"nigeria/ikeja/raw/{self.year}/{self.month}/{file_name}"

        # Create local folder structure
        local_folder = f"./nigeria/ikeja/raw/{self.year}/{self.month}"
        os.makedirs(local_folder, exist_ok=True)
        local_file_path = os.path.join(local_folder, file_name)

        if not self.uploader:
            raise Exception("Uploader not initialized")

        try:
            print(f"Downloading raw file from S3: {s3_path}")
            self.uploader.download_file(s3_path, local_file_path)
            print(f"Downloaded raw file to: {local_file_path}")
            self.file = local_file_path
            return local_file_path
        except Exception as e:
            print(f"Error downloading raw file from S3: {e}")
            raise

    def get_data(self):
        with open(self.file, "r", encoding="utf-8") as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, "lxml")
        outages = soup.find_all("div", class_="col-md-4")
        res = []
        for outage in outages:
            state_class = outage.find(class_=["post-category"])
            date_class = outage.find(class_=["post-date"])
            details = dict()
            if state_class and date_class:
                details["country"] = "Nigeria"
                state = state_class.text
                date = date_class.text
                date = datetime.strptime(date, "%a, %d %b %Y").strftime("%Y-%m-%d")
                details["start"] = date
                info = outage.find("h3", class_="post-title")
                info = info.get_text(separator=" ", strip=True).split(" ")
                i = 0

                details["event_category"] = "historical outage"
                tmp = dict()
                while i < len(info):
                    key = info[i].strip()[:-1]
                    tmp[key] = ""
                    i += 1
                    text = ""
                    while i < len(info) and ":" not in info[i]:
                        text += info[i].strip() + " "
                        i += 1
                    tmp[key] = text.strip()

                if "AFFECTED" in tmp:
                    areas = tmp["AFFECTED"].split(",")
                    details["area_affected"] = {state: areas}

            if details:
                res.append(details)
        return res

    def check_folder(self, type):
        self.folder_path = (
            "./nigeria/ikeja/" + type + "/" + self.year + "/" + self.month
        )
        os.makedirs(self.folder_path, exist_ok=True)

    def save_json(self, data):
        self.check_folder("processed")
        file_name = f"power_outages.NG.ikeja.processed.{self.today}.json"
        file_path = os.path.join(self.folder_path, file_name)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        print(f"Saved processed data to: {file_path}")

        if self.uploader:
            s3_path = f"nigeria/ikeja/processed/{self.year}/{self.month}/{file_name}"
            try:
                self.uploader.upload_file(file_path, s3_path)
                print(f"Uploaded processed file to S3: {s3_path}")
            except Exception as e:
                print(f"Error uploading processed file: {e}")

    def run(self, date=None):
        try:
            self.download_raw_file(date)
        except Exception as e:
            print(f"Failed to download raw file: {e}")
            return

        data = self.get_data()

        self.save_json(data)


if __name__ == "__main__":
    import sys

    # python post_process.py [YYYY-MM-DD]
    date = sys.argv[1] if len(sys.argv) > 1 else None

    if date:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        year = str(date_obj.year)
        month = str(date_obj.month).zfill(2)
    else:
        today = datetime.today()
        year = str(today.year)
        month = str(today.month).zfill(2)
        date = today.strftime("%Y-%m-%d")

    processor = Process_Ikeja(year, month, date)
    processor.run(date)
