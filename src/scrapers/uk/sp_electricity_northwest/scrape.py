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

    url = "https://www.enwl.co.uk/api/power-outages/search"
    limit = 100
    page_number = 1
    all_records = []
    seen_ids = set()

    while True:
        params = {
            "pageSize": limit,
            "pageNumber": page_number,
            "includeCurrent": True,
            "includeResolved": True,
            "includeTodaysPlanned": False,
            "includeFuturePlanned": False,
            "includeCancelledPlanned": False,
        }

        resp = requests.get(url, params=params)
        resp.raise_for_status()
        items = resp.json()["Items"]

        if len(items) == 0:
            break

        # Dedup on faultNumber
        for item in items:
            fault_num = item.get("faultNumber")
            if fault_num not in seen_ids:
                seen_ids.add(fault_num)
                all_records.append(item)

        page_number += 1
        time.sleep(random.uniform(0.5, 1.5))

        if len(items) < limit:
            break

    # Save raw JSON locally
    raw_filename = f"power_outages.GB.sp_electricity_northwest.raw.{today}.json"
    local_path = f"/tmp/{raw_filename}"
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2, ensure_ascii=False)

    print(f"Scraped {len(all_records)} records (deduped by faultNumber)")

    # Upload to volume
    uploader = Uploader("uk")
    volume_path = f"sp_electricity_northwest/raw/{year}/{month}/{raw_filename}"
    uploader.upload_file(local_path, volume_path)

    # Clean up local temp file
    os.remove(local_path)

    return volume_path


if __name__ == "__main__":
    scrape()
