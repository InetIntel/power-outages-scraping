import json
import os
from bs4 import BeautifulSoup
from datetime import datetime


class Process_quetta:

    def __init__(self, year, month, today, file):
        self.year = year
        self.month = month
        self.today = today
        self.file = file

    def parse(self):
        with open(self.file, "r", encoding="utf-8") as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, "html.parser")
        # headers = [th.get_text(strip=True) for th in soup.find_all("th")]
        rows = []
        for tr in soup.find_all("tr")[1:]:
            data = [td.get_text(strip=True) for td in tr.find_all("td")]
            date = str(datetime.strptime(data[2], "%d-%m-%Y").strftime("%Y-%m-%d")) + "_"
            times = data[3].split(",")
            start = datetime.strptime(times[0], '%H-%M-%S')
            end = datetime.strptime(times[1], '%H-%M-%S')
            start_time = datetime.strptime(start, "%H:%M")
            end_time = datetime.strptime(end, "%H:%M")
            tmp = {
                "country": "Pakistan",
                "start": date + start,
                "end": date + end,
                "duration_(hours)": (end_time - start_time).total_seconds() / 3600,
                "event_category": data[4],
                "area_affected": {data[0]: data[1]}
            }
            rows.append(tmp)
            # rows.append(dict(zip(headers, data)))
        return rows

    def check_folder(self, type):
        self.folder_path = "./pakistan/quetta/" + type + "/" + self.year + "/" + self.month
        os.makedirs(self.folder_path, exist_ok=True)

    def save_json(self, data):
        self.check_folder("processed")
        file_name = "power_outages.PK.quetta.processed." + self.today + ".json"
        file_path = os.path.join(self.folder_path, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def run(self):
        data = self.parse()
        self.save_json(data)
        print("Data is processed for quetta.")


if __name__ == "__main__":
    file = ""
    file_list = file.split(".")
    date = file_list[-2]
    date_list = date.split("-")
    year = date_list[0]
    month = date_list[1]
    process = Process_quetta(year, month, date, file)
    process.run()