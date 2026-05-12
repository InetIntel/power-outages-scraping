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

    url = "https://spenergynetworks.opendatasoft.com/api/explore/v2.1/catalog/datasets/distribution-network-live-outages/records"
    limit = 100
    offset = 0
    all_records = []
    seen_ids = set()

    while True:
        params = {
            "limit": limit,
            "offset": offset,
            "apikey": "",
        }

        resp = requests.get(url, params=params)
        resp.raise_for_status()
        results = resp.json()["results"]

        if len(results) == 0:
            break

        # Dedup on incidentreference
        for record in results:
            ref = record.get("incidentreference")
            if ref not in seen_ids:
                seen_ids.add(ref)
                all_records.append(record)

        offset += limit
        time.sleep(random.uniform(0.5, 1.5))

        if len(results) < limit:
            break

    # Save raw JSON locally
    raw_filename = f"power_outages.GB.sp_energy_networks.raw.{today}.json"
    local_path = f"/tmp/{raw_filename}"
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2, ensure_ascii=False)

    print(f"Scraped {len(all_records)} records (deduped by incidentreference)")

    # Upload to volume
    uploader = Uploader("uk")
    volume_path = f"sp_energy_networks/raw/{year}/{month}/{raw_filename}"
    uploader.upload_file(local_path, volume_path)

    # Clean up local temp file
    os.remove(local_path)

    return volume_path


if __name__ == "__main__":
    scrape()
