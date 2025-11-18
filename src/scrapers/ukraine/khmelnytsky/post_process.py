import json
import os
import glob
from datetime import datetime
import lxml.html
from utils.upload import Uploader


class Process_Khmelnytsky:
    def __init__(self, year, month, today, file=None):
        self.year = year
        self.month = month
        self.today = today
        self.file = file
        self.bucket_name = "ukraine"
        self.regions = ["4", "12", "17", "21", "23", "24"]
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
        local_folder = f"./ukraine/khmelnytsky/raw/{self.year}/{self.month}"
        os.makedirs(local_folder, exist_ok=True)

        if not self.uploader:
            raise Exception("Uploader not initialized")

        downloaded_files = []
        for region in self.regions:
            file_name = f"power_outages.UA.khmelnytsky.raw.{date}.{region}.html"
            s3_path = f"ukraine/khmelnytsky/raw/{self.year}/{self.month}/{file_name}"
            local_file_path = os.path.join(local_folder, file_name)

            try:
                self.uploader.download_file(s3_path, local_file_path)
                downloaded_files.append(local_file_path)
            except Exception as e:
                print(f"error downloading raw file for region {region} from S3: {e}")
                # continue with other regions even if one fails
                continue

        return downloaded_files

    def get_data(self):
        # get all HTML files for today
        raw_folder = f"./ukraine/khmelnytsky/raw/{self.year}/{self.month}"
        file_pattern = f"power_outages.UA.khmelnytsky.raw.{self.today}.*.html"
        files = glob.glob(os.path.join(raw_folder, file_pattern))

        if not files:
            print(
                f"no HTML files found in {raw_folder} matching pattern {file_pattern}"
            )
            return []

        date_format = "%d.%m.%Y %H:%M"
        res = []

        for file_path in files:
            print(f"processing file: {file_path}")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                    html_page = lxml.html.fromstring(html_content)

                    # extract planned disconnections from table rows without class attribute
                    planned_disconnections = html_page.xpath("//tbody/tr[not(@class)]")

                    for disconnection in planned_disconnections:
                        try:
                            # Extract data from table cells
                            planned_end_time = "".join(
                                disconnection.xpath(".//td[5]/div//text()")
                            ).strip()
                            start_time = "".join(
                                disconnection.xpath(".//td[4]/div//text()")
                            ).strip()
                            disconnection_type_raw = disconnection.xpath(
                                ".//td[2]//text()"
                            )

                            if (
                                not planned_end_time
                                or not start_time
                                or not disconnection_type_raw
                            ):
                                continue

                            disconnection_type = disconnection_type_raw[0].strip()
                            city_list = disconnection.xpath(
                                './/p[@class="city"]/text()'
                            )

                            # parse dates
                            start_datetime = datetime.strptime(start_time, date_format)
                            end_datetime = datetime.strptime(
                                planned_end_time, date_format
                            )

                            # calculate duration
                            duration = (
                                end_datetime - start_datetime
                            ).total_seconds() / 3600

                            # determine event category
                            if disconnection_type == "Планові":
                                category = "Planned"
                            else:
                                category = "Emergency"

                            line = {
                                "start": start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                                "end": end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                                "duration_(hours)": "{:.2f}".format(duration),
                                "event_category": category,
                                "country": "Ukraine",
                                "areas_affected": city_list,
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
            "./ukraine/khmelnytsky/" + type + "/" + self.year + "/" + self.month
        )
        os.makedirs(self.folder_path, exist_ok=True)

    def save_json(self, data):
        self.check_folder("processed")
        file_name = f"power_outages.UA.khmelnytsky.processed.{self.today}.json"
        file_path = os.path.join(self.folder_path, file_name)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"saved processed data to: {file_path}")

        if self.uploader:
            s3_path = (
                f"ukraine/khmelnytsky/processed/{self.year}/{self.month}/{file_name}"
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

    # python post_process_khmelnytsky.py [YYYY-MM-DD]
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

    processor = Process_Khmelnytsky(year, month, date)
    processor.run(date)
