import json
import os
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
import requests


class ScrapeRajdhaniWeekly:

    def __init__(self, url):
        self.url = url

    def check_folder(self):
        folder_path = "./data"
        os.makedirs(folder_path, exist_ok=True)

    def fetch(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("tbody", {"id": "billDetailsData"})
        return table


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
        week = self.get_week()
        self.save_json(res, week)


    def get_week(self):
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday() + 1)
        end_of_week = start_of_week + timedelta(days=6)
        start_date_str = start_of_week.strftime("%d-%m-%Y")
        end_date_str = end_of_week.strftime("%d-%m-%Y")
        week = start_date_str + "_to_" + end_date_str
        return week

    def save_json(self, data, week):
        self.check_folder()
        file_path = os.path.join("./data", "weekly_outage_report_" + week + ".json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def run(self):
        table = self.fetch()
        self.process(table)


url = "https://www.bsesdelhi.com/web/brpl/weekly-dashboard"
scrapeRajdhaniWeekly = ScrapeRajdhaniWeekly(url)
scrapeRajdhaniWeekly.run()
