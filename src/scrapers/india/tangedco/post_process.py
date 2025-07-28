import os
import json
from bs4 import BeautifulSoup
from datetime import datetime
import glob

class ProcessTangedco:
    def __init__(self, year, month, date, file_path):
        self.year = year
        self.month = month
        self.date = date
        self.file_path = file_path
        self.output_path = f"/data/india/tangedco/processed/{year}/{month}"
        os.makedirs(self.output_path, exist_ok=True)

    def read_file(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                html = f.read()
        except Exception as e:
            print(f"Failed to read HTML: {e}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all("li")
        outage = []

        for item in items:
            try:
                text = item.get_text(strip=True)
                if not text:
                    continue
                data = {
                    "country": "India",
                    "date": self.date,
                    "area_affected": {"unknown": text},
                    "event_category": "Scheduled Maintenance"
                }
                outage.append(data)
            except Exception as e:
                print(f"Bad row: {e}")
                continue

        return outage

    def save(self, data):
        filename = f"power_outages.IND.tangedco.processed.{self.date}.json"
        path = os.path.join(self.output_path, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved: {path} ({len(data)} records)")

    def run(self):
        data = self.read_file()
        self.save(data)

def detect_and_run():
    search_pattern = "/data/india/tangedco/raw/*/*/power_outages.IND.tangedco.raw.*.html"
    files = sorted(glob.glob(search_pattern), key=os.path.getmtime, reverse=True)

    if not files:
        print(f"No raw files found under: {search_pattern}")
        return

    for file_path in files:
        base = os.path.basename(file_path)
        parts = base.split(".")
        if len(parts) < 5:
            print(f"Skipping malformed filename: {base}")
            continue

        try:
            date_str = parts[4]
            year, month, _ = date_str.split("-")
        except Exception as e:
            print(f"Failed to parse filename: {base} ({e})")
            continue

        processor = ProcessTangedco(year, month, date_str, file_path)
        processor.run()

if __name__ == "__main__":
    detect_and_run()
