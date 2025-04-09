import json
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
from india.process_bses_weekly import Process_bses_weekly


class BsesWeekly:

    def __init__(self):
        self.url = "https://www.bsesdelhi.com/web/brpl/weekly-dashboard"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None
        self.year = str(datetime.now().year)
        self.month = str(datetime.now().month).zfill(2)

    def check_folder(self, type):
        self.folder_path = "./india/rajdhani_weekly/" + type + "/" + self.year + "/" + self.month
        os.makedirs(self.folder_path, exist_ok=True)


    def fetch(self):
        response = requests.get(self.url)
        self.check_folder("raw")
        file_name = "power_outages.IND.rajdhani_weekly.raw." + self.today + ".html"
        file_path = os.path.join(self.folder_path, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(response.text)
            print("Raw file is saved for Rajdhani_weekly")
        process = Process_bses_weekly(self.year, self.month, self.today, self.folder_path + "/" + file_name)
        process.run()
        # soup = BeautifulSoup(response.text, "html.parser")
        # table = soup.find("tbody", {"id": "billDetailsData"})
        # return table


    def process(self, table):
        res = []
        all_tr = table.find_all("tr")
        titles = [td.get_text(strip=True) for td in all_tr[1].find_all(["td", "th"])]
        for tr in all_tr[2:]:
            row_data = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            data = {}
            for i in range(len(titles)):
                data[titles[i]] = row_data[i]
            res.append(data)
        self.save_json(res)


    def get_week(self):
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday() + 1)
        end_of_week = start_of_week + timedelta(days=6)
        start_date_str = start_of_week.strftime("%d-%m-%Y")
        end_date_str = end_of_week.strftime("%d-%m-%Y")
        week = start_date_str + "_to_" + end_date_str
        return week

    def save_json(self, data):
        self.check_folder("processed")
        file_path = os.path.join(self.folder_path, "power_outages.IND.rajdhani_weekly.raw." + self.today + ".json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def scrape(self):
        self.fetch()
        # self.process(table)



if __name__ == "__main__":
    bsesWeekly = BsesWeekly()
    bsesWeekly.scrape()
