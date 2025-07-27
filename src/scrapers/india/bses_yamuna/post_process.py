import os
import json
import glob
from datetime import datetime
from bs4 import BeautifulSoup

class BSESYamunaProcessor:
    def __init__(self):
        self.provider = "bses_yamuna"
        self.country = "india"
        self.base_path = "/data"

        # Use same date as in scrape.py for test/debug
        # target = datetime.strptime("25-07-2025", "%d-%m-%Y")

        # today’s date if debug is not used
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

        table_body = soup.find("tbody", id="maintainanceScheduleData")
        if not table_body:
            print("No data rows found in <tbody>")
            return []

        rows = table_body.find_all("tr")
        results = []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 4:
                continue

            division = cols[0].text.strip()
            time_range = cols[1].text.strip()
            reason = cols[2].text.strip()
            area = cols[3].text.strip()

            if "-" not in time_range:
                continue

            start_str, end_str = [t.strip() for t in time_range.split("-")]
            try:
                start_time = datetime.strptime(start_str, "%H:%M")
                end_time = datetime.strptime(end_str, "%H:%M")
            except ValueError:
                continue

            duration = (end_time - start_time).total_seconds() / 60
            if duration < 0:
                duration += 24 * 60

            results.append({
                "country": "India",
                "start": f"{self.today_iso}_{start_time.strftime('%H-%M-%S')}",
                "end": f"{self.today_iso}_{end_time.strftime('%H-%M-%S')}",
                "duration_(mins)": round(duration),
                "event_category": "maintenance schedule",
                "reason": reason,
                "area_affected": {
                    division: [a.strip() for a in area.rstrip(",").split(",") if a.strip()]
                }
            })

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
    BSESYamunaProcessor().process()
