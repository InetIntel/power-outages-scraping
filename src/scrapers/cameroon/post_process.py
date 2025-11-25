import json
import os
from datetime import datetime
from utils.upload import Uploader


class ProcessCameroon:
    def __init__(self, today=None):
        if today is None:
            today_obj = datetime.today()
            self.today = today_obj.strftime("%Y-%m-%d")
            self.year = str(today_obj.year)
            self.month = str(today_obj.month).zfill(2)
        else:
            date_obj = datetime.strptime(today, "%Y-%m-%d")
            self.today = today
            self.year = str(date_obj.year)
            self.month = str(date_obj.month).zfill(2)

        self.bucket_name = "cameroon"
        self.uploader = Uploader(self.bucket_name)

        # all regions
        self.regions = [
            'adamaoua', 'centre', 'douala', 'est', 'extreme_nord',
            'littoral', 'ouest', 'nord', 'nord_ouest', 'sud', 'sud_ouest', 'yaounde'
        ]

    def download_raw_file(self, region):
        file_name = f"power_outages.CM.{region}.raw.{self.today}.json"
        s3_path = f"cameroon/{region}/raw/{self.year}/{self.month}/{file_name}"

        local_folder = f"./cameroon/{region}/raw/{self.year}/{self.month}"
        os.makedirs(local_folder, exist_ok=True)
        local_file_path = os.path.join(local_folder, file_name)

        try:
            self.uploader.download_file(s3_path, local_file_path)
            print(f"[{region.upper()}] - downloaded raw data from S3")
            return local_file_path
        except FileNotFoundError:
            if os.path.exists(local_file_path):
                print(f"[{region.upper()}] - using local raw data (missing from S3)")
                return local_file_path
            else:
                raise

    def process_outage(self, outage, region_name):
        if not outage or not isinstance(outage, dict):
            return None

        details = {
            "country": "Cameroon",
            "event_category": "planned outage"
        }

        # extract district/neighborhood
        if outage.get("quartier"):
            details["district"] = outage["quartier"].strip()

        # extract city
        if outage.get("ville"):
            details["city"] = outage["ville"].strip()

        # extract region
        if outage.get("region"):
            details["region"] = outage["region"].strip()
        else:
            details["region"] = region_name.upper()

        # extract description
        if outage.get("observations"):
            details["description"] = outage["observations"].strip()

        # extract date
        if outage.get("prog_date"):
            details["start_date"] = outage["prog_date"]

        # extract and normalize times (07H00 -> 07:00)
        if outage.get("prog_heure_debut"):
            time_str = outage["prog_heure_debut"].replace("H", ":").replace("h", ":")
            details["start_time"] = time_str

        if outage.get("prog_heure_fin"):
            time_str = outage["prog_heure_fin"].replace("H", ":").replace("h", ":")
            details["end_time"] = time_str

        # create area_affected structure
        district = outage.get("quartier", "").strip()
        city = outage.get("ville", "").strip()
        region_api = outage.get("region", "").strip()

        if district:
            if city:
                details["area_affected"] = {city: [district]}
            elif region_api:
                details["area_affected"] = {region_api: [district]}
            else:
                details["area_affected"] = {region_name.upper(): [district]}

        # only return if we have meaningful data
        if "district" in details or "description" in details:
            return details
        return None

    def process_region_file(self, region):
        try:
            file_path = self.download_raw_file(region)
        except FileNotFoundError as e:
            print(f"[{region.upper()}] - raw file not found: {e}")
            return []
        except Exception as e:
            print(f"[{region.upper()}] - error downloading: {e}")
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                raw_data = json.load(file)
        except json.JSONDecodeError as e:
            print(f"[{region.upper()}] - invalid JSON in raw file: {e}")
            return []
        except Exception as e:
            print(f"[{region.upper()}] - error reading file: {e}")
            return []

        processed_outages = []

        if isinstance(raw_data, dict) and "data" in raw_data:
            outages = raw_data["data"]
        elif isinstance(raw_data, list):
            outages = raw_data
        else:
            print(f"[{region.upper()}] ⚠ Unexpected data format")
            return []

        for outage in outages:
            processed = self.process_outage(outage, region)
            if processed:
                processed_outages.append(processed)

        print(f"[{region.upper()}] ✓ Processed {len(processed_outages)} outages")
        return processed_outages

    def run(self):

        all_outages = []
        successful = 0
        failed = 0

        for region in self.regions:
            outages = self.process_region_file(region)
            if outages is not None:
                all_outages.extend(outages)
                successful += 1
            else:
                failed += 1

        # create consolidated output
        output_data = {
            "metadata": {
                "country": "Cameroon",
                "scrape_date": self.today,
                "total_outages": len(all_outages),
                "regions_processed": successful,
                "regions_failed": failed
            },
            "outages": all_outages
        }

        # save locally
        output_dir = f"./cameroon/processed/{self.year}/{self.month}"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"cameroon.{self.today}.json")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        # upload to S3
        s3_path = f"cameroon/processed/{self.year}/{self.month}/cameroon.{self.today}.json"
        self.uploader.upload_file(output_file, s3_path)
        print(f"uploaded to S3: s3://cameroon/{s3_path}")

        return output_file


def main():
    import sys

    # python post_process.py [YYYY-MM-DD]
    date = sys.argv[1] if len(sys.argv) > 1 else None

    processor = ProcessCameroon(today=date)
    processor.run()


if __name__ == "__main__":
    main()