import requests
import json
import os
import time
import random
from datetime import datetime
from utils.upload import Uploader


REGIONS = [
    "Arklow",
    "Athlone",
    "Ballina",
    "Bandon",
    "Castlebar",
    "Cavan",
    "Clonmel",
    "Cork",
    "Drogheda",
    "Dublin%20Central",
    "Dublin%20North",
    "Dundalk",
    "Dunmanway",
    "Ennis",
    "Enniscorthy",
    "Fermoy",
    "Galway",
    "Kilkenny",
    "Killarney",
    "Killybegs",
    "Letterkenny",
    "Limerick",
    "Longford",
    "Mullingar",
    "Newcastlewest",
    "Portlaoise",
    "Roscrea",
    "Sligo",
    "Thurles",
    "Tralee",
    "Tuam",
    "Tullamore",
    "Waterford",
]


def fetch_outages():
    """
    Fetch power outage data from the ESB Networks API, region by region.
    Paginates at 100 results per page.
    """
    headers = {
        "accept": "application/json",
        "api-subscription-key": "f713e48af3a746bbb1b110ab69113960",
        "captchaoption": "friendlyCaptcha",
    }

    results_per_page = 100
    all_outages = []

    for region in REGIONS:
        page = 1
        while True:
            params = {
                "page": page,
                "results": results_per_page,
                "sort": 3,
                "order": 1,
                "filter": "",
                "rnd": "0.123456",
            }
            url = f"https://api.esb.ie/esbn/powercheck/v1.0/plannergroups/{region}/outages"

            resp = requests.get(url, headers=headers, params=params)

            # 404 means no more pages for this region
            if resp.status_code == 404:
                break

            data = resp.json()

            # Check if there is any outage data
            if "outageDetail" not in data:
                break

            outage_details = data["outageDetail"]
            all_outages.extend(outage_details)
            page += 1

            time.sleep(random.uniform(0.5, 1.5))

            # Last page if fewer results than requested
            if len(outage_details) < results_per_page:
                break

        print(f"Fetched region: {region}")

    return all_outages


def upload_raw(data, today, year, month):
    """
    Save raw JSON data locally and upload to volume via Uploader.
    """
    filename = f"power_outages.IE.esb.raw.{today}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    uploader = Uploader("ireland")
    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    s3_path = f"ireland/raw/{year}/{month}/{filename}"
    uploader.upload_file(local_path, s3_path)
    print(f"Uploaded raw data: {s3_path}")


if __name__ == "__main__":
    today = datetime.today().strftime("%Y-%m-%d")
    year = datetime.today().strftime("%Y")
    month = datetime.today().strftime("%m")

    print("Fetching outage data from ESB Networks API...")
    data = fetch_outages()
    print(f"Fetched {len(data)} total outage records across all regions")

    upload_raw(data, today, year, month)
    print("Done.")
