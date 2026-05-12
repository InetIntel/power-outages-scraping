import json
import os
import time
import random
import requests
from datetime import datetime
from utils.upload import Uploader


def scrape():
    today = datetime.today().strftime("%Y-%m-%d")
    year = str(datetime.today().year)
    month = str(datetime.today().month).zfill(2)

    url = "https://connecteddata.nationalgrid.co.uk/api/3/action/datastore_search"
    limit = 1000
    offset = 0
    all_records = []
    seen_ids = set()

    while True:
        params = {
            "resource_id": "292f788f-4339-455b-8cc0-153e14509d4d",
            "limit": limit,
            "offset": offset,
        }

        resp = requests.get(url, params=params)
        resp.raise_for_status()
        records = resp.json()["result"]["records"]

        if len(records) == 0:
            break

        # Dedup on 'Incident ID'
        for record in records:
            incident_id = record.get("Incident ID")
            if incident_id not in seen_ids:
                seen_ids.add(incident_id)
                all_records.append(record)

        offset += limit
        time.sleep(random.uniform(0.5, 1.5))

        if len(records) < limit:
            break

    # Save raw JSON locally
    raw_filename = f"power_outages.GB.national_grid.raw.{today}.json"
    local_path = f"/tmp/{raw_filename}"
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2, ensure_ascii=False)

    print(f"Scraped {len(all_records)} records (deduped by Incident ID)")

    # Upload to volume
    uploader = Uploader("uk")
    volume_path = f"national_grid/raw/{year}/{month}/{raw_filename}"
    uploader.upload_file(local_path, volume_path)

    # Clean up local temp file
    os.remove(local_path)

    return volume_path


if __name__ == "__main__":
    scrape()
