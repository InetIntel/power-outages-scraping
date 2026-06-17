import json
from datetime import datetime
from pathlib import Path
from utils.upload import Uploader


class TohokuProcessor:
    """
    Processor for Tohoku Electric Power Company (東北電力) outage JSON data.
    Reads a raw JSON file and outputs a processed summary file:
        power_outages.JP.tohoku.processed.YYYY-MM-DD.json
    """

    def __init__(self, data_dir):
        self.provider = "tohoku"
        self.country_code = "JP"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.today = datetime.now()
        self.today_iso = self.today.strftime("%Y-%m-%d")

    def _get_raw_file_path(self):
        """Path to the downloaded raw Tohoku JSON file."""
        filename = f"power_outages.{self.country_code}.{self.provider}.raw.{self.today_iso}.json"
        return self.data_dir / filename

    def _get_output_file_path(self):
        """Path to the processed output JSON file."""
        filename = f"power_outages.{self.country_code}.{self.provider}.processed.{self.today_iso}.json"
        return self.data_dir / filename

    def _parse_outages(self, raw_data):
        """Extract outages from JSON into a consistent structured list."""
        all_outages = []
        entries = raw_data.get("entries", [])
        if not entries:
            print("No entries found in Tohoku JSON data.")
            return all_outages

        for entry in entries:
            details = entry.get("details", [])
            if not details:
                continue

            for d in details:
                start_time = d.get("time")
                end_time = d.get("recovery_time")
                pref = d.get("pref_name")
                city_area = d.get("name", "")
                houses = d.get("count", 0)
                reason = d.get("reason", "")

                start_dt = None
                end_dt = None
                duration = None

                try:
                    year = self.today.year
                    start_dt = datetime.strptime(
                        f"{year}年{start_time}", "%Y年%m月%d日 %H:%M"
                    )
                except Exception:
                    pass

                try:
                    year = self.today.year
                    end_dt = datetime.strptime(
                        f"{year}年{end_time}", "%Y年%m月%d日 %H:%M"
                    )
                except Exception:
                    pass

                if start_dt and end_dt:
                    duration = round((end_dt - start_dt).total_seconds() / 3600, 2)

                outage = {
                    "start": start_time,
                    "end": end_time,
                    "duration_(hours)": duration,
                    "prefecture": pref,
                    "location": city_area,
                    "houses_affected": houses,
                    "reason": reason.strip(),
                }

                all_outages.append(outage)

        return all_outages

    def run(self, input_path):
        """Parse and save processed JSON."""
        with open(input_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        outages = self._parse_outages(raw_data)
        output_path = self._get_output_file_path()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(outages, f, ensure_ascii=False, indent=2)

        print(f"\nProcessed {len(outages)} outages -> {output_path.name}")
        return output_path


def find_latest_raw_file(uploader, bucket, prefix):
    """Return the key of the most recent raw JSON file in the bucket.

    The shared-volume client doesn't expose mtime, but the filenames embed
    an ISO date (YYYY-MM-DD), so a lexicographic sort is also chronological.
    """
    response = uploader.client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    contents = response.get("Contents", [])
    if not contents:
        print("No files found in the raw folder.")
        return None

    latest = sorted(contents, key=lambda x: x["Key"], reverse=True)[0]["Key"]
    print(f"Latest raw file found: {latest}")
    return latest


def main():
    bucket = "japan"
    prefix = "japan/tohoku/raw/"
    local_dir = Path("/app/data")
    local_dir.mkdir(parents=True, exist_ok=True)

    uploader = Uploader(bucket)
    today = datetime.now().strftime("%Y-%m-%d")
    expected_filename = f"power_outages.JP.tohoku.raw.{today}.json"
    expected_key = prefix + expected_filename

    # Step 1: Try today's file first, fall back to latest available
    local_raw_path = local_dir / expected_filename
    try:
        print(f"Checking for today's file: {expected_key}")
        uploader.download_file(expected_key, str(local_raw_path))
    except FileNotFoundError:
        print("Today's file not found — looking for latest available file...")
        raw_key = find_latest_raw_file(uploader, bucket, prefix)
        if not raw_key:
            print("No raw files available to process.")
            return
        local_raw_path = local_dir / Path(raw_key).name
        uploader.download_file(raw_key, str(local_raw_path))

    print(f"Downloaded raw file -> {local_raw_path}")

    # Step 2: Process using your same logic
    processor = TohokuProcessor(local_dir)
    processed_path = processor.run(local_raw_path)

    # Step 3: Upload processed file to the shared volume
    processed_key = f"japan/tohoku/processed/{processed_path.name}"
    uploader.upload_file(str(processed_path), processed_key)
    print(f"Uploaded processed file -> {processed_key}")

    print("Tohoku post-processing complete.")


if __name__ == "__main__":
    main()
