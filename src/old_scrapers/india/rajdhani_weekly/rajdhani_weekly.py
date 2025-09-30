import json
import os
from datetime import datetime, timedelta
import requests
from india.rajdhani_weekly.process_rajdhani_weekly import Process_rajdhani_weekly


class RajdhaniWeekly:

    def __init__(self):
        self.url = "https://www.bsesdelhi.com/web/brpl/weekly-dashboard"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None
        self.year = str(datetime.now().year)
        self.month = str(datetime.now().month).zfill(2)

    def check_folder(self, type):
        self.folder_path = "./india/rajdhani_weekly/" + type + "/" + self.year + "/" + self.month
        os.makedirs(self.folder_path, exist_ok=True)

    def scrape(self):
        # Fetch data with proper error handling
        response = requests.get(self.url)
        if response.status_code == 200:
            # Save raw HTML file
            self.check_folder("raw")
            file_name = "power_outages.IND.rajdhani_weekly.raw." + self.today + ".html"
            file_path = os.path.join(self.folder_path, file_name)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(response.text)
                print("Raw file is saved for Rajdhani_weekly")
            
            # Process immediately - both steps are required
            process = Process_rajdhani_weekly(self.year, self.month, self.today, file_path)
            process.run()
        else:
            print(f"Failed to retrieve webpage. Status code: {response.status_code}")
            return

    def get_week(self):
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday() + 1)
        end_of_week = start_of_week + timedelta(days=6)
        start_date_str = start_of_week.strftime("%d-%m-%Y")
        end_date_str = end_of_week.strftime("%d-%m-%Y")
        week = start_date_str + "_to_" + end_date_str
        return week


if __name__ == "__main__":
    rajdhani_weekly = RajdhaniWeekly()
    rajdhani_weekly.scrape()