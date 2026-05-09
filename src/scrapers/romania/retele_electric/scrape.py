import requests
import json
import os
import time
import random
from datetime import datetime
from utils.upload import Uploader


def fetch_outages():
    """
    Fetch power outage data from the Retele Electrice ArcGIS API.
    Fetches both Accidental and Planned outages with pagination at 1000 records.
    """
    url = "https://services-eu1.arcgis.com/ZugzWQbNk6XT3BMo/arcgis/rest/services/OutagesMapViewLayer/FeatureServer/0/query"

    base_params = {
        "f": "json",
        "returnGeometry": "false",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "*",
        "maxRecordCountFactor": 4,
        "orderByFields": "num_cli_di DESC",
        "outSR": 102100,
        "resultRecordCount": 1000,
        "cacheHint": "true",
    }

    results_per_page = 1000
    all_data = []

    # Fetch both Accidental and Planned outages
    for outage_type in ["Accidental", "Planned"]:
        offset = 0
        while True:
            params = dict(base_params)
            params["where"] = f"causa_disa_en = '{outage_type}'"
            params["resultOffset"] = offset
            params["resultRecordCount"] = results_per_page

            try:
                resp = requests.get(url, params=params)
                resp.raise_for_status()
            except Exception as e:
                print(f"Error fetching {outage_type} outages: {e}")
                break

            features = resp.json().get("features", [])

            if len(features) == 0:
                break

            # Extract attributes from features
            all_data.extend(f.get("attributes", {}) for f in features)

            if len(features) < results_per_page:
                break

            offset += results_per_page
            time.sleep(random.uniform(0.5, 1.5))

        print(f"Fetched {outage_type} outages (total so far: {len(all_data)})")

    return all_data


def upload_raw(data, today, year, month):
    """
    Save raw JSON data locally and upload to volume via Uploader.
    """
    filename = f"power_outages.RO.retele_electric.raw.{today}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    uploader = Uploader("romania")
    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    s3_path = f"retele_electric/raw/{year}/{month}/{filename}"
    uploader.upload_file(local_path, s3_path)
    print(f"Uploaded raw data: {s3_path}")


if __name__ == "__main__":
    today = datetime.today().strftime("%Y-%m-%d")
    year = datetime.today().strftime("%Y")
    month = datetime.today().strftime("%m")

    print("Fetching outage data from Retele Electrice API...")
    data = fetch_outages()
    print(f"Fetched {len(data)} total outage records")

    upload_raw(data, today, year, month)
    print("Done.")
