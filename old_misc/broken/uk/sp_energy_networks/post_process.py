import json
import os
import sys
from datetime import datetime
from utils.upload import Uploader


def post_process(date_str=None):
    if date_str is None:
        date_str = datetime.today().strftime("%Y-%m-%d")

    parts = date_str.split("-")
    year = parts[0]
    month = parts[1]

    uploader = Uploader("uk")

    raw_filename = f"power_outages.GB.sp_energy_networks.raw.{date_str}.json"
    raw_path = f"sp_energy_networks/raw/{year}/{month}/{raw_filename}"
    local_raw = f"/tmp/{raw_filename}"

    uploader.download_file(raw_path, local_raw)

    with open(local_raw, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded {len(data)} raw records for {date_str}")

    # Save processed JSON
    processed_filename = (
        f"power_outages.GB.sp_energy_networks.processed.{date_str}.json"
    )
    local_processed = f"/tmp/{processed_filename}"
    with open(local_processed, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    processed_path = f"sp_energy_networks/processed/{year}/{month}/{processed_filename}"
    uploader.upload_file(local_processed, processed_path)

    # Clean up local temp files
    os.remove(local_raw)
    os.remove(local_processed)

    print(f"Processed {len(data)} records -> {processed_path}")
    return processed_path


if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    post_process(date_arg)
