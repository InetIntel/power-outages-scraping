import requests
import os
import time
import random
import json
from datetime import datetime
#from utils import Uploader

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

def upload():
    """
    Upload raw data json to minio storage.
    """
    pass

if __name__ == "__main__":

    # get data from api
    current_outages = get_data()

    # save locally to docker container as json file
    save_json(current_outages)

    # upload raw outage data to minio storage
    #upload()