import requests
import json
import os
from datetime import datetime
from utils.upload import Uploader


def fetch_outages():
    """
    Fetch power outage data from the Stoerungsauskunft API.
    Uses basic auth (frontend/frontend) and SectorType=1 for power outages.
    """
    url = "https://api-public.stoerungsauskunft.de/api/v1/public/outages"

    params = {"SectorType": "1"}

    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "Origin": "https://xn--strungsauskunft-9sb.de",
        "Referer": "https://xn--strungsauskunft-9sb.de/",
    }

    auth = ("frontend", "frontend")

    resp = requests.get(url, params=params, headers=headers, auth=auth)
    resp.raise_for_status()

    data = resp.json()
    return data


def upload_raw(data, today, year, month):
    """
    Save raw JSON data locally and upload to volume via Uploader.
    """
    filename = f"power_outages.DE.stoerungsauskunft.raw.{today}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    uploader = Uploader("germany")
    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    s3_path = f"stoerungsauskunft/raw/{year}/{month}/{filename}"
    uploader.upload_file(local_path, s3_path)
    print(f"Uploaded raw data: {s3_path}")


if __name__ == "__main__":
    today = datetime.today().strftime("%Y-%m-%d")
    year = datetime.today().strftime("%Y")
    month = datetime.today().strftime("%m")

    print("Fetching outage data from Stoerungsauskunft API...")
    data = fetch_outages()
    print(f"Fetched {len(data)} outage records")

    upload_raw(data, today, year, month)
    print("Done.")
