import json
import os
import glob
from datetime import datetime
import lxml.html
from utils.upload import Uploader


class Process_Vinnytsia:
    def __init__(self, year, month, today, file=None):
        self.year = year
        self.month = month
        self.today = today
        self.file = file
        self.bucket_name = "ukraine"
        self.regions = [
            "23",
            "25",
            "26",
            "27",
            "29",
            "30",
            "31",
            "32",
            "33",
            "35",
            "36",
            "37",
            "38",
            "39",
            "41",
            "42",
            "43",
            "45",
            "46",
            "47",
            "48",
            "50",
            "51",
            "52",
            "53",
            "55",
            "56",
            "57",
        ]
        self.types = ["planned", "emergency"]
        try:
            self.uploader = Uploader(self.bucket_name)
        except Exception as e:
            print(f"error initializing uploader: {e}")
            self.uploader = None

    def download_raw_files(self, date=None):
        if date is None:
            date = self.today
        else:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            self.year = str(date_obj.year)
            self.month = str(date_obj.month).zfill(2)
            self.today = date

        # create local folder structure
        local_folder = f"./ukraine/vinnytsia/raw/{self.year}/{self.month}"
        os.makedirs(local_folder, exist_ok=True)

        if not self.uploader:
            raise Exception("uploader not initialized")

        downloaded_files = []
        for region in self.regions:
            for type in self.types:
                file_name = (
                    f"power_outages.UA.vinnytsia.raw.{date}.{region}.{type}.html"
                )
                s3_path = f"ukraine/vinnytsia/raw/{self.year}/{self.month}/{file_name}"
                local_file_path = os.path.join(local_folder, file_name)

                try:
                    print(f"downloading raw file from S3: {s3_path}")
                    self.uploader.download_file(s3_path, local_file_path)
                    print(f"downloaded raw file to: {local_file_path}")
                    downloaded_files.append(local_file_path)
                except Exception as e:
                    print(
                        f"error downloading raw file for region {region}, type {type} from S3: {e}"
                    )
                    # continue with other files even if one fails
                    continue

        return downloaded_files

    def get_data(self):
        # get all HTML files for today
        raw_folder = f"./ukraine/vinnytsia/raw/{self.year}/{self.month}"
        file_pattern = f"power_outages.UA.vinnytsia.raw.{self.today}.*.html"
        files = glob.glob(os.path.join(raw_folder, file_pattern))

        if not files:
            print(
                f"no HTML files found in {raw_folder} matching pattern {file_pattern}"
            )
            return []

        date_format = "%Y-%m-%d %H:%M:%S"
        res = []

        for file_path in files:
            print(f"processing file: {file_path}")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    planned_disconnections = lxml.html.fromstring(content).xpath(
                        '//tr[@class="row"]'
                    )

                    for disconnection in planned_disconnections:
                        try:
                            # extract data from table cells
                            planned_end_time = (
                                disconnection.xpath(
                                    './/td[@class="accend_plan"]/text()'
                                )
                                or [""]
                            )[0].strip()
                            actual_end_time = (
                                disconnection.xpath(
                                    './/td[@class="accend_fact"]/text()'
                                )
                                or [""]
                            )[0].strip()
                            start_time = (
                                disconnection.xpath('.//td[@class="accbegin"]/text()')
                                or [""]
                            )[0].strip()
                            disconnection_type = (
                                disconnection.xpath('.//td[@class="acctype"]/text()')
                                or [""]
                            )[0].strip()
                            village_list_raw = (
                                disconnection.xpath('.//td[@class="city_list"]/text()')
                                or [""]
                            )[0]

                            if not start_time:
                                continue

                            # parse village list
                            village_list = []
                            if village_list_raw:
                                areas = [
                                    area.strip()
                                    for area in village_list_raw.split(",")
                                    if area.strip()
                                ]
                                village_list = [
                                    {"type": "city", "area": area} for area in areas
                                ]

                            # prefer actual end time over planned end time
                            end_time_string = (
                                actual_end_time if actual_end_time else planned_end_time
                            )

                            # parse dates
                            start_datetime = datetime.strptime(start_time, date_format)

                            if end_time_string:
                                try:
                                    end_datetime = datetime.strptime(
                                        end_time_string, date_format
                                    )
                                    duration = (
                                        end_datetime - start_datetime
                                    ).total_seconds() / 3600
                                    end_str = end_datetime.strftime("%Y-%m-%d %H:%M:%S")
                                    duration_str = "{:.2f}".format(duration)
                                except Exception:
                                    end_str = "unknown"
                                    duration_str = "unknown"
                            else:
                                end_str = "unknown"
                                duration_str = "unknown"

                            # determine event category
                            if disconnection_type == "Планове відключення":
                                category = "Planned"
                            else:
                                category = "Emergency"

                            line = {
                                "start": start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                                "end": end_str,
                                "duration_(hours)": duration_str,
                                "event_category": category,
                                "country": "Ukraine",
                                "areas_affected": village_list,
                            }
                            res.append(line)

                        except Exception as e:
                            print(f"error processing in {file_path}: {e}")
                            continue

            except Exception as e:
                print(f"error processing file {file_path}: {e}")
                continue

        return res

    def check_folder(self, type):
        self.folder_path = (
            "./ukraine/vinnytsia/" + type + "/" + self.year + "/" + self.month
        )
        os.makedirs(self.folder_path, exist_ok=True)

    def save_json(self, data):
        self.check_folder("processed")
        file_name = f"power_outages.UA.vinnytsia.processed.{self.today}.json"
        file_path = os.path.join(self.folder_path, file_name)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"saved processed data to: {file_path}")

        if self.uploader:
            s3_path = (
                f"ukraine/vinnytsia/processed/{self.year}/{self.month}/{file_name}"
            )
            try:
                self.uploader.upload_file(file_path, s3_path)
                print(f"uploaded processed file to S3: {s3_path}")
            except Exception as e:
                print(f"error uploading processed file: {e}")

    def run(self, date=None):
        try:
            self.download_raw_files(date)
        except Exception as e:
            print(f"failed to download raw files: {e}")
            # continue anyway in case files exist locally
            pass

        data = self.get_data()

        if data:
            self.save_json(data)
        else:
            print("no data extracted from HTML files")


if __name__ == "__main__":
    import sys

    # python post_process_vinnytsia.py [YYYY-MM-DD]
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

    processor = Process_Vinnytsia(year, month, date)
    processor.run(date)
