import os
import json
import glob
from bs4 import BeautifulSoup
from datetime import datetime

class TataProcessor:
    def __init__(self):
        self.provider = "tata"
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
                    "area_affected": {
                        cols[0].text.strip(): [
                            x.strip() for x in cols[1].text.split(",") if x.strip()
                        ]
                    }
                })
            except Exception as e:
                print(f"Bad row: {e}")
                continue
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
    TataProcessor().run()
