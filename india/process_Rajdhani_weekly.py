import json
import os
from bs4 import BeautifulSoup



class Process_Rajdhani_weekly:

    def __init__(self, year, month, today, file):
        self.year = year
        self.month = month
        self.today = today
        self.file = file

    def get_table(self):
        with open(self.file, "r", encoding="utf-8") as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, "html.parser")
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
        self.save_json(res)

    def check_folder(self, type):
        self.folder_path = "./india/rajdhani_weekly/" + type + "/" + self.year + "/" + self.month
        os.makedirs(self.folder_path, exist_ok=True)

    def save_json(self, data):
        self.check_folder("processed")
        file_path = os.path.join(self.folder_path,
                                 "power_outages.IND.rajdhani_weekly.processed." + self.today + ".json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def run(self):
        table = self.get_table()
        self.process(table)
        print("Data is processed for Rajdhani_weekly.")


if __name__ == "__main__":
    file = ""
    file_list = file.split(".")
    date = file_list[-2]
    date_list = date.split("-")
    year = date_list[0]
    month = date_list[1]
    process = Process_Rajdhani_weekly(year, month, date, file)
    process.run()
