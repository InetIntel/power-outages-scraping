import json
import os
import re
from datetime import datetime
from utils.upload import Uploader


class Process_Cherkasy:
    def __init__(self, year, month, today, file=None):
        self.year = year
        self.month = month
        self.today = today
        self.file = file
        self.bucket_name = "ukraine"
        try:
            self.uploader = Uploader(self.bucket_name)
        except Exception as e:
            print(f"error initializing uploader: {e}")
            self.uploader = None

    def download_raw_file(self, date=None):
        if date is None:
            date = self.today
        else:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            self.year = str(date_obj.year)
            self.month = str(date_obj.month).zfill(2)
            self.today = date

        file_name = f"power_outages.UA.cherkasy.raw.{date}.json"
        s3_path = f"ukraine/cherkasy/raw/{self.year}/{self.month}/{file_name}"

        # Create local folder structure
        local_folder = f"./ukraine/cherkasy/raw/{self.year}/{self.month}"
        os.makedirs(local_folder, exist_ok=True)
        local_file_path = os.path.join(local_folder, file_name)

        if not self.uploader:
            raise Exception("uploader not initialized")

        try:
            self.uploader.download_file(s3_path, local_file_path)
            self.file = local_file_path
            return local_file_path
        except Exception as e:
            print(f"error downloading raw file from S3: {e}")
            raise

    def get_data(self):
        with open(self.file, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Define the date format
        date_format = "%d.%m.%Y %H:%M"
        res = []

        for disconnection_item in data:
            if isinstance(disconnection_item.get("DISCONNECTIONS"), list):
                print(
                    f"skipping empty disconnection item: {disconnection_item.get('DISCONNECTIONS')}"
                )
                continue

            disconnections = disconnection_item.get("DISCONNECTIONS", {})
            if not isinstance(disconnections, dict):
                continue

            for number, disconnection in disconnections.items():
                try:
                    start = disconnection.get("DATE_START", "")
                    end_raw = disconnection.get("DATE_STOP", "")

                    if not start or not end_raw:
                        continue

                    # remove anything after ( in DATE_STOP
                    end = end_raw.split("(")[0].strip()

                    # parse the date strings into datetime objects
                    start_time = datetime.strptime(start, date_format)
                    stop_time = datetime.strptime(end, date_format)

                    # calculate duration in hours
                    duration = (stop_time - start_time).total_seconds() / 3600

                    event_category = disconnection.get("DISCONN_TYPE", "")
                    areas_affected_raw = disconnection.get("ADDRESS", "")

                    # regular expression to find text between <br> tags
                    matches = re.findall(r"<br>(.*?)<br>", areas_affected_raw)
                    cleaned_matches_areas = [
                        match.strip() for match in matches if match.strip()
                    ]

                    # determine event category
                    if event_category == "Планове":
                        category = "Planned"
                    elif event_category in ["Аварійне", "Аварiйне"]:
                        category = "Emergency"
                    else:
                        category = "Outage Schedule"

                    line = {
                        "start": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "end": stop_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "duration_(hours)": "{:.2f}".format(duration),
                        "event_category": category,
                        "country": "Ukraine",
                        "areas_affected": cleaned_matches_areas,
                    }
                    res.append(line)

                except Exception as e:
                    print(f"Error processing disconnection {number}: {e}")
                    continue

        return res

    def check_folder(self, type):
        self.folder_path = (
            "./ukraine/cherkasy/" + type + "/" + self.year + "/" + self.month
        )
        os.makedirs(self.folder_path, exist_ok=True)

    def save_json(self, data):
        self.check_folder("processed")
        file_name = f"power_outages.UA.cherkasy.processed.{self.today}.json"
        file_path = os.path.join(self.folder_path, file_name)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"saved processed data to: {file_path}")

        if self.uploader:
            s3_path = f"ukraine/cherkasy/processed/{self.year}/{self.month}/{file_name}"
            try:
                self.uploader.upload_file(file_path, s3_path)
                print(f"uploaded processed file to S3: {s3_path}")
            except Exception as e:
                print(f"error uploading processed file: {e}")

    def run(self, date=None):
        try:
            self.download_raw_file(date)
        except Exception as e:
            print(f"failed to download raw file: {e}")
            return

        data = self.get_data()

        self.save_json(data)


if __name__ == "__main__":
    import sys

    # python post_process_cherkasy.py [YYYY-MM-DD]
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

    processor = Process_Cherkasy(year, month, date)
    processor.run(date)
