import json
import os
import sys
from datetime import datetime
from utils.upload import Uploader


BUCKET_NAME = "romania"
PROVIDER_NAME = "retele_electric"
COUNTRY_CODE = "RO"


def download_raw(today, year, month):
    """
    Download raw JSON data from volume via Uploader.
    """
    uploader = Uploader(BUCKET_NAME)
    filename = f"power_outages.{COUNTRY_CODE}.{PROVIDER_NAME}.raw.{today}.json"
    s3_path = f"{PROVIDER_NAME}/raw/{year}/{month}/{filename}"
    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    uploader.download_file(s3_path, local_path)
    with open(local_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def deduplicate(data):
    """
    Deduplicate outage records based on fid0.
    Keeps the last occurrence of each unique fid0.
    """
    seen = {}
    for record in data:
        key = record.get("fid0")
        if key is not None:
            seen[key] = record
        else:
            # Keep records without a fid0 as-is
            seen[id(record)] = record
    return list(seen.values())


def upload_processed(data, today, year, month):
    """
    Save processed JSON data locally and upload to volume via Uploader.
    """
    filename = f"power_outages.{COUNTRY_CODE}.{PROVIDER_NAME}.processed.{today}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    uploader = Uploader(BUCKET_NAME)
    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    s3_path = f"{PROVIDER_NAME}/processed/{year}/{month}/{filename}"
    uploader.upload_file(local_path, s3_path)
    print(f"Uploaded processed data: {s3_path}")


if __name__ == "__main__":
    # Support optional date argument: python post_process.py [YYYY-MM-DD]
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        date_obj = datetime.today()

    today = date_obj.strftime("%Y-%m-%d")
    year = date_obj.strftime("%Y")
    month = date_obj.strftime("%m")

    print(f"Downloading raw data for {today}...")
    raw_data = download_raw(today, year, month)
    print(f"Downloaded {len(raw_data)} raw records")

    processed_data = deduplicate(raw_data)
    print(f"After deduplication: {len(processed_data)} records")

    upload_processed(processed_data, today, year, month)
    print("Done.")
