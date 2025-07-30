import os
import json
import glob
import calendar
from bs4 import BeautifulSoup
from datetime import datetime

class MahavitaranProcessor:
    def __init__(self):
        self.provider = "mahavitaran"
        self.country = "india"
        self.base_path = "/data"
        
        # Use a specific debug date (optional)
        # target = datetime.strptime("05-06-2025", "%d-%m-%Y")  # DEBUG: hardcoded test date
        
        # today's date if debug is not used
        target = datetime.now()
        
        self.today_iso = target.strftime("%Y-%m-%d")
        self.year = target.strftime("%Y")
        self.month = target.strftime("%m")

    def create_folder(self, data_type):
        folder_path = os.path.join(self.base_path, self.country, self.provider, data_type, self.year, self.month)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def find_latest_raw_file(self):
        raw_folder = self.create_folder("raw")
        today_file = glob.glob(os.path.join(raw_folder, f"*{self.today_iso}.html"))
        if today_file:
            return today_file[0]
        all_files = sorted(glob.glob(os.path.join(raw_folder, "*.html")), key=os.path.getmtime, reverse=True)
        return all_files[0] if all_files else None

    def parse_html(self, html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        rows = soup.select("#wo_shd_table tbody tr")
        if not rows:
            print("No data rows found in <tbody>")
            return []

        results = []
        last_day = calendar.monthrange(int(self.year), int(self.month))[1]

        # Define week ranges for the current month
        week_ranges = {
            "Week 1": (1, 7),
            "Week 2": (8, 14),
            "Week 3": (15, 21),
            "Week 4": (22, 28),
            "Week 5": (29, last_day)
        }

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 24:  # Ensure we have enough columns
                continue

            try:
                region = cols[0].text.strip()
                zone = cols[1].text.strip()
                circle = cols[2].text.strip()
                division = cols[3].text.strip()

                # Process data for each week (5 weeks per month)
                for i in range(5):
                    offset = 4 + i * 4  # Column offset for each week's data
                    try:
                        total_outages = int(cols[offset].text.strip())
                        duration_mins = int(cols[offset + 1].text.strip())
                        outage_hrs = cols[offset + 2].text.strip()
                        supply_hrs = cols[offset + 3].text.strip()
                    except (ValueError, IndexError):
                        continue

                    week_label = f"Week {i+1}"
                    day_start, day_end = week_ranges[week_label]
                    
                    try:
                        start_dt = datetime(int(self.year), int(self.month), day_start)
                        end_dt = datetime(int(self.year), int(self.month), day_end)
                    except ValueError as e:
                        print(f"Failed to parse date for {week_label}: {e}")
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
                        "week": week_label,
                        "area_affected": {
                            "region": region,
                            "zone": zone,
                            "circle": circle,
                            "division": division
                        }
                    })

            except Exception as e:
                print(f"Failed to parse row: {e}")
                continue

        return results

    def save_json(self, data):
        folder = self.create_folder("processed")
        filename = f"power_outages.IND.{self.provider}.processed.{self.today_iso}.json"
        path = os.path.join(folder, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved processed JSON: {path}")
        print(f"Records saved: {len(data)}")

    def process(self):
        raw_folder = self.create_folder("raw")
        not_found_files = glob.glob(os.path.join(raw_folder, f"404_{self.today_iso}.txt"))
        
        if not_found_files:
            log_path = os.path.join(self.create_folder("processed"), f"no_data_found.{self.today_iso}.log")
            with open(log_path, "w") as f:
                f.write(f"No outage schedule found for {self.today_iso}. See {os.path.basename(not_found_files[0])} in raw folder.")
            print(f"No data to process. Log saved at: {log_path}")
            return

        raw_file = self.find_latest_raw_file()
        if not raw_file:
            print("No raw file found.")
            return

        print(f"Processing file: {raw_file}")
        parsed_data = self.parse_html(raw_file)
        self.save_json(parsed_data)

if __name__ == "__main__":
    MahavitaranProcessor().process()