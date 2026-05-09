import json
import os
import requests
from datetime import datetime
from utils.upload import Uploader


def scrape():
    today = datetime.today().strftime("%Y-%m-%d")
    year = str(datetime.today().year)
    month = str(datetime.today().month).zfill(2)

    url = "http://api.sse.com/powerdistribution/network/v3/api/faults"

    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    faults = data["faults"]

    # Dedup on incidentreference
    seen_ids = set()
    all_records = []
    for fault in faults:
        ref = fault.get("incidentreference")
        if ref not in seen_ids:
            seen_ids.add(ref)
            all_records.append(fault)

    # Save raw JSON locally
    raw_filename = f"power_outages.GB.scottish_southern.raw.{today}.json"
    local_path = f"/tmp/{raw_filename}"
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2, ensure_ascii=False)

    print(f"Scraped {len(all_records)} records (deduped by incidentreference)")

    # Upload to volume
    uploader = Uploader("uk")
    volume_path = f"scottish_southern/raw/{year}/{month}/{raw_filename}"
    uploader.upload_file(local_path, volume_path)

    # Clean up local temp file
    os.remove(local_path)

    return volume_path


if __name__ == "__main__":
    scrape()
