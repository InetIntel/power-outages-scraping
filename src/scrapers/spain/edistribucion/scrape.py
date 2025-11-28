import requests
import os
import time
import random
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from utils import Uploader


def get_data():
    """
    Get current outage data from the API.
    """
    base_url = "https://ineuportalgis.enel.com/server/rest/services/Hosted/ESP_Prod_power_cut_View/FeatureServer/0/query"
    last_id = -1
    all_features = []

    while True:
        params = {
            "f": "json",
            "where": f"objectid1 > {last_id}",
            "outFields": "*",
            "returnGeometry": "true",
            "orderByFields": "objectid1 ASC",
            "resultRecordCount": 2000,
        }
        try:
            r = requests.get(base_url, params=params, timeout=30)
            r.raise_for_status()
            data = r.json()
        except Exception as e:  # Catches any exception type
            print(f"Request failed: {e}")
            break

        features = data.get("features", [])
        if not features:
            break
        all_features.extend(features)
        last_id = features[-1]["attributes"]["objectid1"]
        time.sleep(random.uniform(0.5, 1.5))

    return all_features

def upload_raw(raw_data: List[Dict[str, Any]]):
    """
    Upload raw data json to minio storage.
    """
    now = datetime.now(timezone.utc)
    current_year = f"{now.year}"
    current_month = f"{now.month:02d}"
    current_day = f"{now.day:02d}"
    current_hour = f"{now.hour:02d}"
    current_minute = f"{now.minute:02d}"
    current_second = f"{now.second:02d}"

    # first save raw data locally to container as json
    filename = f'power_outages.ES.edistribucion.raw.{current_year}-{current_month}-{current_day}-{current_hour}-{current_minute}-{current_second}.json'
    with open(filename, 'w') as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=4)

    # now upload json to minio
    uploader = Uploader('spain')
    local_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        filename
    )
    s3_path = f"edistribucioin/raw/{current_year}/{current_month}/{filename}"
    uploader.upload_file(local_path, s3_path)

def save_json(data):
    """
    Save current raw outage data to local
    docker container as a json file.
    """
    # Directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Folder to store data
    data_dir = os.path.join(script_dir, "data")

    # Ensure the directory exists
    os.makedirs(data_dir, exist_ok=True)

    # Build the filename with timestamp
    now = datetime.now()
    current_year = f"{now.year}"
    current_month = f"{now.month:02d}"
    current_day = f"{now.day:02d}"
    file_name = f'power_outages.ES.edistribucion.raw.{current_year}-{current_month}-{current_day}.json'
    file_path = os.path.join(data_dir, file_name)

    # Save the file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved JSON to: {file_path}")
    except Exception as e:
        print(f"Failed to save JSON: {e}")

def get_pre_existing_outages():
    """
    Get json of pre-existing outages data in "current_outages" folder in minio bucket.
    """
    # create uploader object
    bucket_name = 'spain'
    uploader = Uploader(bucket_name)

    # specify local path to download file
    local_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'current_outages.json'
    )

    # Download file if it exists, else create list to store new data to upload
    try:
        s3_path = 'edistribucion/current_outages/current_outages.json'
        uploader.download_file(s3_path, local_path)
    except FileNotFoundError as e:
        new_current_outages_list = []
        with open('current_outages.json', 'w') as f:
            json.dump(new_current_outages_list, f, ensure_ascii=False, indent=4)

def update_current_outages(pre_existing_outages, new_data):

    # Map current_outages by "OBJECTID" attribute for faster searching
    current_by_id: Dict[Any, Dict[str, Any]] = {
        o["attributes"]["objectid1"]: o for o in pre_existing_outages if "objectid1" in o["attributes"]
    }

    # collect new "current_outages" as we compare to new raw data
    updated_current_outages: List[Dict[str, Any]] = []

    # keep track of ongoing outage ids to know if any "current" outages are resolved
    ongoing_outage_ids = set()

    # now iterate through "new_data" to update "current_outages"
    for outage in new_data:

        # get id of outage
        outage_id = outage["attributes"]["objectid1"]
        if outage_id == None:
            continue # ignore outages with no id
        ongoing_outage_ids.add(outage_id)

        # if outage is not present in current_outages, add to "updated_current_outages" and
        # give it an attribute "ioda_status": "in_progress", and move on to next outage
        existing = current_by_id.get(outage_id)
        if existing is None:
            outage["ioda_status"] = "in_progress"
            if not outage['attributes']['interruption_date']:
                timestamp_ms = int(time.time() * 1000)
                outage['attributes']['interruption_date'] = timestamp_ms
            updated_current_outages.append(outage)
            continue # move on to next outage

        # else if outage is present already, update "last_edited_date" attribute, take max of
        # "CLIENTES_AFECTADOS", add to "updated_current_outages" and move on to next outage
        updated_outage = dict(existing)
        updated_outage["attributes"] = dict(existing["attributes"])
        updated_outage["attributes"]["affected_client"] = max(0, existing["attributes"]["affected_client"], outage["attributes"]["affected_client"])
        if "last_edited_date" in outage["attributes"]:
            updated_outage["attributes"]["last_edited_date"] = outage["attributes"]["last_edited_date"]
        updated_current_outages.append(updated_outage)

    # all "current_outages" that did not appear in new data, change "ioda_status" to "resolved"
    for outage in pre_existing_outages:
        if outage["attributes"]["objectid1"] not in ongoing_outage_ids:
            completed_outage = dict(outage)
            completed_outage["ioda_status"] = "resolved"
            if not completed_outage['attributes']['last_edited_date']:
                timestamp_ms = int(time.time() * 1000)
                completed_outage['attributes']['last_edited_date'] = timestamp_ms
            updated_current_outages.append(completed_outage)

    return updated_current_outages

if __name__ == "__main__":

    # get data from api
    new_data = get_data()
    print(len(new_data))

    # upload new raw data to minio
    upload_raw(new_data)

    # get pre-existing outages from minio
    get_pre_existing_outages()
    with open('current_outages.json', 'r') as file:
        pre_existing_outages = json.load(file)

    # use new outage data to update pre_existing outages
    updated_current_outages = update_current_outages(pre_existing_outages, new_data)