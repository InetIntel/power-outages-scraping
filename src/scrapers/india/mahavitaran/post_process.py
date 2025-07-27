import os
import json
import glob
import calendar
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

class MahavitaranProcessor:
    def __init__(self, year, month, day, file_path):
        self.year = year
        self.month = month
        self.day = day
        self.today = f"{year}-{month}-{day}"
        self.file_path = file_path

    def create_folder(self):
        folder = os.path.join("/data", "india", "mahavitaran", "processed", self.year, self.month, self.day)
        os.makedirs(folder, exist_ok=True)
        return folder

    def parse_table(self):
        with open(self.file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file.read(), "html.parser")

        rows = soup.select("#wo_shd_table tbody tr")
        results = []
        last_day = calendar.monthrange(int(self.year), int(self.month))[1]

        week_ranges = {
            "Week 1": (1, 7),
            "Week 2": (8, 14),
            "Week 3": (15, 21),
            "Week 4": (22, 28),
            "Week 5": (29, last_day)
        }

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 24:
                continue

            try:
                region = cols[0].text.strip()
                zone = cols[1].text.strip()
                circle = cols[2].text.strip()
                division = cols[3].text.strip()

                for i in range(5):
                    offset = 4 + i * 4
                    try:
                        total_outages = int(cols[offset].text.strip())
                        duration_mins = int(cols[offset + 1].text.strip())
                        outage_hrs = cols[offset + 2].text.strip()
                        supply_hrs = cols[offset + 3].text.strip()
                    except ValueError:
                        continue

                    week_label = f"Week {i+1}"
                    day_start, day_end = week_ranges[week_label]
                    try:
                        start_dt = datetime(int(self.year), int(self.month), day_start)
                        end_dt = datetime(int(self.year), int(self.month), day_end)
                    except ValueError as e:
                        print(f"Failed to parse row for {week_label}: {e}")
                        continue

                    results.append({
                        "country": "India",
                        "start": start_dt.strftime("%Y-%m-%d_00-00-00"),
                        "end": end_dt.strftime("%Y-%m-%d_23-59-59"),
                        "duration_(mins)": duration_mins,
                        "total_outages": total_outages,
                        "per_feeder_outage_hours": outage_hrs,
                        "per_feeder_supply_hours": supply_hrs,
                        "event_category": "weekly outage summary",
                        "area_affected": {
                            region: {
                                zone: {
                                    circle: [
                                        division
                                    ]
                                }
                            }
                        }
                    })

            except Exception as e:
                print(f"Failed to parse row: {e}")
                continue

        return results

    def save_json(self, data):
        folder = self.create_folder()
        filename = f"power_outages.IND.mahavitaran.processed.{self.today}.json"
        path = os.path.join(folder, filename)

        existing = []
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception as e:
                print(f"Warning reading existing JSON: {e}")

        combined = existing + data

        with open(path, "w", encoding="utf-8") as f:
            json.dump(combined, f, indent=2, ensure_ascii=False)
        print(f"Saved processed JSON: {path} with {len(combined)} records.")

    def run(self):
        data = self.parse_table()
        if data:
            self.save_json(data)

if __name__ == "__main__":
    for file in glob.glob("/data/india/mahavitaran/raw/*/*/*/*.html"):
        parts = file.split(".")
        if len(parts) < 6 or "_" not in parts[-2]:
            print(f"Skipping invalid file: {file}")
            continue
        try:
            date_str = parts[-2].split("_")[0]
            year, month, day = date_str.split("-")
        except ValueError:
            print(f"Invalid date format in file: {file}")
            continue

        processor = MahavitaranProcessor(year, month, day, file)
        processor.run()
