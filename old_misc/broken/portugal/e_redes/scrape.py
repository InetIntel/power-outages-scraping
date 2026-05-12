import requests
import json
import os
import time
import random
from datetime import datetime
from utils.upload import Uploader


def fetch_outages():
    """
    Fetch power outage data from the E-REDES OpenDataSoft API.
    Paginates at 20 records per request.
    """
    url = "https://e-redes.opendatasoft.com/api/explore/v2.1/catalog/datasets/outages-per-geography/records"
    limit = 20
    offset = 0
    all_records = []

    while True:
        params = {
            "limit": limit,
            "offset": offset,
        }

        resp = requests.get(url, params=params)
        resp.raise_for_status()

        data = resp.json()
        results = data.get("results", [])

        if len(results) == 0:
            break

        all_records.extend(results)
        offset += limit

        time.sleep(random.uniform(0.5, 1.5))

        # Last page if fewer results than requested
        if len(results) < limit:
            break

    return all_records


def upload_raw(data, today, year, month):
    """
    Save raw JSON data locally and upload to volume via Uploader.
    """
    filename = f"power_outages.PT.e_redes.raw.{today}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    uploader = Uploader("portugal")
    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    s3_path = f"e_redes/raw/{year}/{month}/{filename}"
    uploader.upload_file(local_path, s3_path)
    print(f"Uploaded raw data: {s3_path}")


if __name__ == "__main__":
    today = datetime.today().strftime("%Y-%m-%d")
    year = datetime.today().strftime("%Y")
    month = datetime.today().strftime("%m")

    print("Fetching outage data from E-REDES API...")
    data = fetch_outages()
    print(f"Fetched {len(data)} outage records")

    upload_raw(data, today, year, month)
    print("Done.")
