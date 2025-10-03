import json
import os
from bs4 import BeautifulSoup
from datetime import datetime
from utils.upload import Uploader


class Process_Ikeja:
    def __init__(self, year, month, today, file):
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
            except Exception as e:
                print(f"Error uploading processed file: {e}")

    def run(self):
        if self.uploader:
            raw_file_name = os.path.basename(self.file)
            s3_path = f"nigeria/ikeja/raw/{self.year}/{self.month}/{raw_file_name}"
            try:
                self.uploader.upload_file(self.file, s3_path)
            except Exception as e:
                print(f"Error uploading raw file: {e}")

        data = self.get_data()
        self.save_json(data)
