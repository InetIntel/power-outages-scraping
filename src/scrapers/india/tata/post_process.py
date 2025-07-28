import os
import json
from bs4 import BeautifulSoup
from datetime import datetime
import glob

class TataProcessor:
    def __init__(self, file_path, date):
        self.file_path = file_path
        self.date = date
        self.year, self.month = date.split("-")[:2]
        self.output_dir = f"/data/india/tata/processed/{self.year}/{self.month}"
        os.makedirs(self.output_dir, exist_ok=True)

    def parse(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        data = []
        for row in soup.select("tbody#tbodyid tr"):
            cols = row.find_all("td")
            if len(cols) < 5:
                continue
            try:
                start = datetime.strptime(cols[3].text.strip(), "%B %d, %Y %H:%M")
                end = datetime.strptime(cols[4].text.strip(), "%B %d, %Y %H:%M")
                duration = int((end - start).total_seconds() / 3600)
                data.append({
                    "country": "India",
                    "start": start.strftime("%Y-%m-%d_%H-%M-%S"),
                    "end": end.strftime("%Y-%m-%d_%H-%M-%S"),
                    "duration_(hours)": duration,
                    "event_category": cols[2].text.strip() or "unknown",
                    "area_affected": {cols[0].text.strip(): [x.strip() for x in cols[1].text.split(",")]}
                })
            except Exception as e:
                print(f"Bad row: {e}")
                continue
        return data

    def save(self, data):
        name = f"power_outages.IND.tata.processed.{self.date}.json"
        path = os.path.join(self.output_dir, name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Saved: {path} ({len(data)} records)")

    def run(self):
        data = self.parse()
        self.save(data)

def detect_and_run():
    pattern = "/data/india/tata/raw/*/*/power_outages.IND.tata.raw.*.html"
    files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
    if not files:
        print("No raw Tata files found.")
        return
    for file_path in files:
        date = os.path.basename(file_path).split(".")[4]
        TataProcessor(file_path, date).run()

if __name__ == "__main__":
    detect_and_run()
