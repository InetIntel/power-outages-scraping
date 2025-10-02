import os
import json
import glob
from bs4 import BeautifulSoup
from datetime import datetime


class Process_tataddl:
    def __init__(self):
        self.provider = "tataddl"
        self.country = "india"
        self.base_path = "/data"
        self.today = datetime.now()
        self.today_str = self.today.strftime("%Y-%m-%d")
        self.year = self.today.strftime("%Y")
        self.month = self.today.strftime("%m")

    def create_folder(self, kind):
        path = os.path.join(self.base_path, self.country, self.provider, kind, self.year, self.month)
        os.makedirs(path, exist_ok=True)
        return path

    def find_latest_raw_file(self):
        raw_folder = self.create_folder("raw")
        today_file = glob.glob(os.path.join(raw_folder, f"*{self.today_str}.html"))
        if today_file:
            return today_file[0]
        all_files = sorted(glob.glob(os.path.join(raw_folder, "*.html")), key=os.path.getmtime, reverse=True)
        return all_files[0] if all_files else None

    def check_for_scrape_failure(self):
        raw_folder = self.create_folder("raw")
        return os.path.exists(os.path.join(raw_folder, f"404_{self.today_str}.txt"))
    
    def parse(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        table = soup.find(id="DivContent")
        data = []
        if table:
            rows = table.find_all("tr")
            # Ignore the first row (header)
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) < 9:
                    continue  # skip incomplete rows
                row_data = {
                    "s_no": cols[0].text.strip(),
                    "discom": cols[1].text.strip(),
                    "distt": cols[2].text.strip(),
                    "zone": cols[3].text.strip(),
                    "description": cols[4].text.strip(),
                    "datetime_from": cols[5].text.strip(),
                    "datetime_to": cols[6].text.strip(),
                    "area_affected": cols[7].text.strip(),
                    "total_duration_hrs": cols[8].text.strip()
                }
                data.append(row_data)
        return data

    def save(self, data):
        folder = self.create_folder("processed")
        path = os.path.join(folder, f"power_outages.IND.{self.provider}.processed.{self.today_str}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Saved: {path} ({len(data)} records)")

    def save_log(self):
        log_folder = self.create_folder("processed")
        log_path = os.path.join(log_folder, f"no_data_found.{self.today_str}.log")
        with open(log_path, "w") as f:
            f.write(f"No outage data found for {self.today_str}. Scraper reported a failure.\n")
        print(f"No data to process. Log saved: {log_path}")

    def run(self):
        if self.check_for_scrape_failure():
            self.save_log()
            return

        file_path = self.find_latest_raw_file()
        if not file_path:
            print("No raw HTML file found.")
            return

        data = self.parse(file_path)
        self.save(data)

if __name__ == "__main__":
    # Build file path robustly
    # raw_dir = os.path.join(os.path.dirname(__file__), "raw", "2025", "09")
    # file_name = "power_outages.IND.tataddl.raw.2025-09-26.html"
    # file = os.path.join(raw_dir, file_name)
    # file_list = file_name.split(".")
    # date = file_list[-2]
    # date_list = date.split("-")
    # year = date_list[0]
    # month = date_list[1]
    process = Process_tataddl().run()

