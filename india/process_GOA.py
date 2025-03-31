import json
import os
from bs4 import BeautifulSoup
from datetime import datetime


class Process_GOA:

    def __init__(self, year, month, today, file):
        self.year = year
        self.month = month
        self.today = today
        self.file = file

    def get_table(self):
        with open(self.file, "r", encoding="utf-8") as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, "html.parser")

        table = soup.find_all('table')
        rows = table[0].find_all("tr")
        data = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 5:
                date = cols[1].get_text(strip=True)
                date = datetime.strptime(date, "%d-%m-%Y")
                date = date.strftime("%Y-%m-%d")
                start = cols[4].get_text(strip=True).replace(":", "-")
                end = cols[4].get_text(strip=True).replace(":", "-")
                time1 = datetime.strptime(start, '%H-%M-%S')
                time2 = datetime.strptime(end, '%H-%M-%S')
                duration = (time1 - time2).total_seconds() / 3600
                outage_data = {
                    "country": "India",
                    "start": date + "_" + start,
                    "end": date + "_" + end,
                    "duration_(hours)": 5,
                    "event_category": "planned power outage",
                    "area_affected": cols[3].get_text(strip=True).split(", ")
                }
                data.append(outage_data)

        return data


    def check_folder(self, type):
        self.folder_path = "./india/goa/" + type + "/" + self.year + "/" + self.month
        os.makedirs(self.folder_path, exist_ok=True)

    def save_json(self, data):
        self.check_folder("processed")
        file_path = os.path.join(self.folder_path,
                                 "power_outages.IND.goa.processed." + self.today + ".json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def run(self):
        data = self.get_table()
        self.save_json(data)
        print("Data is processed for GOA.")


if __name__ == "__main__":
    file = ""
    file_list = file.split(".")
    date = file_list[-2]
    date_list = date.split("-")
    year = date_list[0]
    month = date_list[1]
    process = Process_GOA(year, month, date, file)
    process.run()
