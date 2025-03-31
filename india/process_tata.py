
import json
import os
from bs4 import BeautifulSoup
from datetime import datetime



class Process_tata:

    def __init__(self, year, month, today, file):
        self.year = year
        self.month = month
        self.today = today
        self.file = file


    def check_folder(self, type):
        self.folder_path = "./india/tata/" + type + "/" + self.year + "/" + self.month
        os.makedirs(self.folder_path, exist_ok=True)


    def save_json(self, data):
        self.check_folder("processed")
        file_path = os.path.join(self.folder_path,
                                 "power_outages.IND.tata.processed." + self.today + ".json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)


    def get_data(self):
        with open(self.file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
        rows = soup.select("tbody#tbodyid tr")
        data = []
        for row in rows:
            cols = row.find_all("td")
            start_time = datetime.strptime(cols[3].text, "%B %d, %Y %H:%M")
            end_time = datetime.strptime(cols[4].text, "%B %d, %Y %H:%M")
            row_data = {
                "country": "India",
                "start": start_time.strftime("%Y-%m-%d_%H-%M-%S"),
                "end": end_time.strftime("%Y-%m-%d_%H-%M-%S"),
                "duration_(hours)": int((end_time - start_time).total_seconds() / 3600),
                "event_category": cols[2].text,
                # "REASON": columns[2].text,
                "area_affected": {cols[0].text: cols[1].text.split(",")}
            }
            # for i in range(len(cols)):
            #     row_data[titles[i]] = cols[i].text
            data.append(row_data)
        return data


    def run(self):
        data = self.get_data()
        self.save_json(data)


if __name__ == "__main__":
    file = ""
    file_list = file.split(".")
    date = file_list[-2]
    date_list = date.split("-")
    year = date_list[0]
    month = date_list[1]
    process = Process_tata(year, month, date, file)
    process.run()
