import os
import json
from datetime import datetime, timezone
import math
from utils import Uploader
from typing import Any, Dict, List, Optional

def get_existing_outages(bucket_name, provider_name):
    """
    Get json of pre-existing outages data in "current_outages" folder in minio bucket.
    """
    # create uploader instance
    uploader = Uploader(bucket_name)

    # specify local path to download file
    local_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'current_outages.json'
    )

    # Download file if it exists, else create list to store new data to upload
    try:
        s3_path = f'{provider_name}/current_outages/current_outages.json'
        uploader.download_file(s3_path, local_path)
    except FileNotFoundError as e:
        new_current_outages_list = []
        with open('current_outages.json', 'w') as f:
            json.dump(new_current_outages_list, f, ensure_ascii=False, indent=4)

def get_resolved_outages(current_outages):
    """
    Takes in current outage data. Collects outages that are
    "resolved" and ready to be moved into long term storage.
    """
    resolved_outages = [] # collect resolved outages ready to post process
    updated_current_outages = [] # collect outages still in progress to keep in 'current_outages.json'

    for outage in current_outages:
        if outage['ioda_status'] == 'resolved':
            resolved_outages.append(outage)
        elif outage['ioda_status'] == 'in_progress':
            updated_current_outages.append(outage)

    return resolved_outages, updated_current_outages

def upload_current_outages(current_outages: List[Dict[str, Any]], bucket_name, provider_name):

    filename = 'current_outages.json'

    # save current outages
    with open(filename, 'w') as f:
        json.dump(current_outages, f, ensure_ascii=False, indent=4)

    # upload json to minio
    uploader = Uploader(bucket_name)
    local_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'current_outages.json'
    )
    s3_path = f"{provider_name}/current_outages/{filename}"
    uploader.upload_file(local_path, s3_path)

def process_data(resolved_outages):
    """
    Process resolved outage raw data.
    """

    # store processed outage data as it's built
    processed_outages = []

    # iterate through raw outage data
    for outage in resolved_outages:

        # get start time
        start_timestamp = outage['ioda_detection_date']
        start_dt = datetime.fromtimestamp(start_timestamp / 1000, tz=timezone.utc)
        formatted_start_dt = start_dt.strftime('%Y-%m-%d_%H-%M-%S')

        # get end time
        end_timestamp = outage['ioda_update_date']
        end_dt = datetime.fromtimestamp(end_timestamp / 1000, tz=timezone.utc)
        formatted_end_dt = end_dt.strftime('%Y-%m-%d_%H-%M-%S')

        # calculate duration
        duration_hours = math.ceil(abs(int(end_timestamp) - int(start_timestamp)) / 3600000)

        # get event category
        if type(outage['attributes']['des_cause_en']) == str:
            event_category = outage['attributes']['des_cause_en']
        else:
            event_category = 'Unplanned'

        processed_outage = {
            'country': 'Spain',
            'start_utc': formatted_start_dt,
            'end_utc': formatted_end_dt,
            'duration_(hours)': duration_hours,
            'event_category': event_category,
            'clients_affected': outage['attributes']['affected_client'],
            'area_affected': outage['attributes']['municipality']
        }
        processed_outages.append(processed_outage)

    return processed_outages

def upload_processed_data(new_processed_data, current_datetime, bucket_name, provider_name):
    """
    Download processed data locally to container as a json file
    then upload the json file to minio for long term storage.
    """

    # create uploader object
    uploader = Uploader(bucket_name)

    # date time data for file name/location in minio
    current_year = current_datetime['current_year']
    current_month = current_datetime['current_month']
    current_day = current_datetime['current_day']

    # get already processed data file to append to
    try:
        local_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'old_processed_data.json'
        )
        filename = f'power_outages.ES.{provider_name}.processed.{current_year}-{current_month}-{current_day}.json'
        s3_path = f'{provider_name}/processed/{current_year}/{current_month}/{filename}'
        uploader.download_file(s3_path, local_path)
        with open('old_processed_data.json', 'r') as file:
            old_processed_data = json.load(file)
    except FileNotFoundError as e:
        old_processed_data = []
    if not old_processed_data:
        old_processed_data = []

    # add new processed data to list
    old_processed_data.extend(new_processed_data)
    all_data = old_processed_data

    # save updated json
    filename = f'power_outages.ES.{provider_name}.processed.{current_year}-{current_month}-{current_day}.json'
    with open(filename, 'w') as file:
        json.dump(all_data, file, ensure_ascii=False, indent=4)

    # upload new json to minio
    local_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        filename
    )
    s3_path = f'{provider_name}/processed/{current_year}/{current_month}/{filename}'
    uploader.upload_file(local_path, s3_path)

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

    # load current ongoing outage data
    get_existing_outages(bucket_name='spain', provider_name='edistribucion')
    with open('current_outages.json', 'r') as file:
        current_outages = json.load(file)

    # parse out "resolved" outages and remove them from the current outage file
    resolved_outages, updated_current_outages = get_resolved_outages(current_outages)

    # upload new 'current_outages.json' with resolved outages removed
    upload_current_outages(updated_current_outages, bucket_name='spain', provider_name='edistribucion')

    # parse resolved outage data and format for minio storage
    processed_data = process_data(resolved_outages)

    # upload processed data to minio storage
    upload_processed_data(processed_data, current_datetime, bucket_name='spain', provider_name='edistribucion')