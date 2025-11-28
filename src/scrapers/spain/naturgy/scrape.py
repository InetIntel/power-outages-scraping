import requests
import os
import time
import random
import json
from datetime import datetime, timezone
from typing import Any, Dict, List
from utils import Uploader

def get_data():
    """
    Get current outage data from the API.
    """
    base_url = "https://gisoperaciones.ufd.es/server/rest/services/Averias/Avisos_VistaPublica/FeatureServer/0/query"
    last_id = -1
    all_features = []

    while True:
        params = {
            "f": "json",
            "where": f"OBJECTID > {last_id}",
            "outFields": "*",
            "returnGeometry": "true",
            "outSR": 4326,
            "orderByFields": "OBJECTID ASC",
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
        last_id = features[-1]["attributes"]["OBJECTID"]
        time.sleep(random.uniform(0.5, 1.5))

    return all_features

def upload_raw(raw_data: List[Dict[str, Any]], current_datetime):
    """
    Upload raw data json from local docker container to minio storage.
    """
    # get date for file naming
    current_year = current_datetime['current_year']
    current_month = current_datetime['current_month']
    current_day = current_datetime['current_day']

    # save raw data locally to container as json
    filename = f'power_outages.ES.naturgy.raw.{current_year}-{current_month}-{current_day}.json'
    with open(filename, 'w') as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=4)

    # now upload json to minio
    uploader = Uploader('spain')
    local_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        filename
    )
    s3_path = f"naturgy/raw/{current_year}/{current_month}/{filename}"
    uploader.upload_file(local_path, s3_path)

def upload_current_outages(current_outages: List[Dict[str, Any]]):
    """
    Save 'current_outages' as a json file then upload it to minio.
    """

    # save current outages
    filename = 'current_outages.json'
    with open(filename, 'w') as f:
        json.dump(current_outages, f, ensure_ascii=False, indent=4)

    # upload json to minio
    uploader = Uploader('spain')
    local_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'current_outages.json'
    )
    s3_path = f"naturgy/current_outages/{filename}"
    uploader.upload_file(local_path, s3_path)

def update_current_outages(pre_existing_outages, new_data):
    """
    Update current outages to contain data from the most recent api call.
    Outages that just appeared for the first time are added to current outage file.
    Outages that just stopped appearing are marked as resolved and later collected by 'post_process.py'.
    """

    # Map current_outages by "OBJECTID" attribute for faster searching
    current_by_id: Dict[Any, Dict[str, Any]] = {
        o["attributes"]["OBJECTID"]: o for o in pre_existing_outages if "OBJECTID" in o["attributes"]
    }

    # collect updated "current_outage" data
    updated_current_outages: List[Dict[str, Any]] = []

    # keep track of ongoing outage ids to know if any "current" outages are resolved
    # if an outage id does not appear in newest api return then it is resolved
    ongoing_outage_ids = set()

    # now iterate through "new_data" to update "current_outages"
    for outage in new_data:

        # get id of outage
        outage_id = outage["attributes"]["OBJECTID"]
        if outage_id == None:
            continue # ignore outages with no id
        ongoing_outage_ids.add(outage_id)

        # if outage is not present in current_outages, add to "updated_current_outages" and
        # give it an attribute "ioda_status": "in_progress", and move on to next outage
        existing = current_by_id.get(outage_id)
        if existing is None:
            outage["ioda_status"] = "in_progress"
            # If raw data doesn't contain a start datetime,
            # say it started now since it just appeared for the first time.
            if not outage['attributes']['FECHA_DETECCION']:
                timestamp_ms = int(time.time() * 1000)
                outage['attributes']['FECHA_DETECCION'] = timestamp_ms
            updated_current_outages.append(outage)
            continue

        # if outage is present already, update "last_edited_date" attribute, take max of
        # "CLIENTES_AFECTADOS", add to "updated_current_outages" and move on to next outage
        updated_outage = dict(existing)
        updated_outage["attributes"] = dict(existing["attributes"])
        updated_outage["attributes"]["CLIENTES_AFECTADOS"] = max(0, existing["attributes"]["CLIENTES_AFECTADOS"], outage["attributes"]["CLIENTES_AFECTADOS"])
        if "last_edited_date" in outage["attributes"]:
            updated_outage["attributes"]["last_edited_date"] = outage["attributes"]["last_edited_date"]
        updated_current_outages.append(updated_outage)

    # All "current_outages" that did not appear in new data, change
    # "ioda_status" to "resolved", the post processor will collect them.
    for outage in pre_existing_outages:
        if outage["attributes"]["OBJECTID"] not in ongoing_outage_ids:
            completed_outage = dict(outage)
            completed_outage["ioda_status"] = "resolved"
            # if it doesn't have a resolved date, mark it as now since it just stopped appearing in api
            if not completed_outage['attributes']['last_edited_date']:
                timestamp_ms = int(time.time() * 1000)
                completed_outage['attributes']['last_edited_date'] = timestamp_ms
            updated_current_outages.append(completed_outage)

    return updated_current_outages

def get_pre_existing_current_outages():
    """
    Get json of ongoing outages data in "current_outages" folder in minio bucket.
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
        s3_path = 'naturgy/current_outages/current_outages.json'
        uploader.download_file(s3_path, local_path)
    except FileNotFoundError as e:
        new_current_outages_list = []
        with open('current_outages.json', 'w') as f:
            json.dump(new_current_outages_list, f, ensure_ascii=False, indent=4)

def get_pre_existing_raw_outages(current_datetime):
    """
    Get json of pre-existing raw outages data for today from minio.
    If no pre-existing data, return [].
    """
    # create uploader object
    bucket_name = 'spain'
    uploader = Uploader(bucket_name)
    file_name = f"power_outages.ES.naturgy.raw.{current_datetime['current_year']}-{current_datetime['current_month']}-{current_datetime['current_day']}.json"

    # specify local path to download file
    local_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), file_name
    )

    # Get data if file exists, else create list to store new data to upload
    try:
        s3_path = f"naturgy/raw/{current_datetime['current_year']}/{current_datetime['current_month']}/{file_name}"
        uploader.download_file(s3_path, local_path)
        with open(file_name, 'r') as file:
            pre_existing_raw_outages = json.load(file)
        if not pre_existing_raw_outages:
            pre_existing_raw_outages = []
    except FileNotFoundError as e:
        pre_existing_raw_outages = []

    # return current raw data to append to
    return pre_existing_raw_outages

def update_raw_data(pre_existing_raw_outage_data, new_raw_outage_data):
    """
    Takes in today's pre-existing raw data from minio and new raw data that just returned from api.
    Returns a new updated raw data file including previously stored and new raw data.
    """

    # store all object id's, pre-existing and new
    all_ids = set()

    # index the old raw data by object id
    indexed_old_raw_outages = {}
    for outage in pre_existing_raw_outage_data:
        id = outage["attributes"]["OBJECTID"]
        indexed_old_raw_outages[id] = outage
        all_ids.add(id)

    # index the new raw data by object id
    indexed_new_raw_outages = {}
    for outage in new_raw_outage_data:
        id = outage["attributes"]["OBJECTID"]
        indexed_new_raw_outages[id] = outage
        all_ids.add(id)

    # list to store new updated raw outage data
    updated_raw_outage_data = []

    # iterate through each outage by id
    for id in all_ids:

        # if outage just started
        if id in indexed_new_raw_outages.keys() and id not in indexed_old_raw_outages.keys():
            outage = indexed_new_raw_outages[id]
            outage['outage_ended_today'] = False
            updated_raw_outage_data.append(outage)

        # if outage just ended
        elif id in indexed_old_raw_outages.keys() and id not in indexed_new_raw_outages.keys():
            outage = indexed_old_raw_outages[id]
            outage['outage_ended_today'] = True
            updated_raw_outage_data.append(outage)

        # if outage is ongoing
        else:
            previous_outage_data = indexed_old_raw_outages[id]
            new_outage_data = indexed_new_raw_outages[id]
            num_people_affected = max(0, previous_outage_data['attributes']['CLIENTES_AFECTADOS'], new_outage_data['attributes']['CLIENTES_AFECTADOS'])
            outage = new_outage_data
            outage['attributes']['CLIENTES_AFECTADOS'] = num_people_affected
            outage['outage_ended_today'] = False
            updated_raw_outage_data.append(outage)

    return updated_raw_outage_data

if __name__ == "__main__":

    # get datetime data once and pass it into functions as needed so it's consistent
    now = datetime.now(timezone.utc)
    current_datetime = {
        'current_year': f"{now.year}",
        'current_month': f"{now.month:02d}",
        'current_day': f"{now.day:02d}",
        'current_hour': f"{now.hour:02d}",
        'current_minute': f"{now.minute:02d}",
        'current_second': f"{now.second:02d}",
    }

    # get current day's raw data file from minio
    pre_existing_raw_outages = get_pre_existing_raw_outages(current_datetime)

    # get new data from api
    new_raw_data = get_data()

    # update pre-existing raw outage file with new data from api
    updated_raw_data = update_raw_data(pre_existing_raw_outages, new_raw_data)

    # upload new raw data to minio
    upload_raw(updated_raw_data, current_datetime)

    # get pre-existing outages from minio
    get_pre_existing_current_outages()
    with open('current_outages.json', 'r') as file:
        pre_existing_outages = json.load(file)

    # use new outage data to update pre_existing outages
    updated_current_outages = update_current_outages(pre_existing_outages, new_raw_data)

    # upload updated current outages to mino
    upload_current_outages(updated_current_outages)
