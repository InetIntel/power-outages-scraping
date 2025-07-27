import os
import json
import glob
from bs4 import BeautifulSoup
from datetime import datetime

class GoaProcessor:
    def __init__(self):
        self.provider = "goa"
        self.country = "india"
        self.base_path = "/data"

        # Use current date in ISO format for consistency
        target_date = datetime.now()
        self.today_iso = target_date.strftime("%Y-%m-%d")
        self.year = target_date.strftime("%Y")
        self.month = target_date.strftime("%m")

    def create_folder(self, data_type):
        folder = os.path.join(self.base_path, self.country, self.provider, data_type, self.year, self.month)
        os.makedirs(folder, exist_ok=True)
        return folder

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

        tables = soup.find_all("table")
        if not tables:
            print("No tables found in page.")
            return []

        rows = tables[0].find_all("tr")
        results = []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) > 5:
                try:
                    date = datetime.strptime(cols[1].text.strip(), "%d-%m-%Y").strftime("%Y-%m-%d")
                    start = cols[4].text.strip().replace(":", "-")
                    end = cols[5].text.strip().replace(":", "-")
                    start_time = datetime.strptime(start, "%H-%M")
                    end_time = datetime.strptime(end, "%H-%M")
                    duration = (end_time - start_time).total_seconds() / 3600
                    if duration < 0:
                        duration += 24

                    results.append({
                        "country": "India",
                        "start": f"{date}_{start_time.strftime('%H-%M-%S')}",
                        "end": f"{date}_{end_time.strftime('%H-%M-%S')}",
                        "duration_(hours)": round(duration, 2),
                        "event_category": "planned power outage",
                        "area_affected": cols[3].get_text(strip=True).split(", ")
                    })
                except Exception as e:
                    print(f"Skipping row due to parsing error: {e}")
                    continue

        return results

    def save_json(self, data):
        folder = self.create_folder("processed")
        file_path = os.path.join(folder, f"power_outages.IND.{self.provider}.processed.{self.today_iso}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved processed JSON: {file_path}")
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
        parsed = self.parse_html(raw_file)
        self.save_json(parsed)

if __name__ == "__main__":
    GoaProcessor().process()