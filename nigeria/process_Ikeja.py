import json
import os
from bs4 import BeautifulSoup
from datetime import datetime


class Process_Ikeja:

    def __init__(self, year, month, today, file):
        self.year = year
        self.month = month
        self.today = today
        self.file = file

    def get_data(self):
        with open(self.file, "r", encoding="utf-8") as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, "html.parser")
        outages = soup.find_all('div', class_='col-md-4')
        res = []
        for outage in outages:
            state_class = outage.find(class_=['post-category'])
            date_class = outage.find(class_=['post-date'])
            details = dict()
            if state_class:
                details["country"] = "Nigeria"
                state = state_class.text
                date = date_class.text
                date = datetime.strptime(date, "%a, %d %b %Y").strftime("%Y-%m-%d")
                details["start"] = date
                info = outage.find('h3', class_='post-title')
                info = info.get_text(separator=" ", strip=True).split(" ")
                i = 0

                details["event_category"] = "historical outage"
                tmp = dict()
                while i < len(info):
                    key = info[i].strip()[:-1]
                    tmp[key] = ""
                    text = ""
                    i += 1
                    while i < len(info) and ":" not in info[i]:
                        text += info[i].strip() + " "
                        i += 1
                    tmp[key] = text.strip()
                areas = tmp["AFFECTED"].split(",")
                details["area_affected"] = {state: areas}
            res.append(details)
        return res

    def check_folder(self, type):
        self.folder_path = "./nigeria/ikeja/" + type + "/" + self.year + "/" + self.month
        os.makedirs(self.folder_path, exist_ok=True)

    def save_json(self, data):
        self.check_folder("processed")
        file_path = os.path.join(self.folder_path,
                                 "power_outages.IND.goa.processed." + self.today + ".json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def run(self):
        data = self.get_data()
        self.save_json(data)
        print("Data is processed for Ikeja.")


if __name__ == "__main__":
    file = ""
    file_list = file.split(".")
    date = file_list[-2]
    date_list = date.split("-")
    year = date_list[0]
    month = date_list[1]
    process = Process_Ikeja(year, month, date, file)
    process.run()