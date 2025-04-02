import json
import os
from bs4 import BeautifulSoup
from datetime import datetime


class Process_BSES:

    def __init__(self, year, month, today, file):
        self.year = year
        self.month = month
        self.today = today
        self.file = file


    def check_folder(self, provider, type):
        self.folder_path = "./india/" + provider + "/" + type + "/" + self.year + "/" + self.month
        os.makedirs(self.folder_path, exist_ok=True)

    def save_json(self, data, provider):
        self.check_folder(provider, "processed")
        file_name = "power_outages.IND." + provider + ".processed." + self.today + ".json"
        file_path = os.path.join(self.folder_path, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def get_data(self):
        with open(self.file, "r", encoding="utf-8") as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find("table", class_="table table-bordered table-striped")
        table_rows = table.find_all("tr") if table else []
        return table_rows

    def process(self, table_rows, provider):
        res = []
        for row in table_rows[2:]:
            columns = row.find_all("td")
            division = columns[0].text
            hours = columns[1].text.split("-")
            start = datetime.strptime(hours[0], "%H:%M")
            end = datetime.strptime(hours[1], "%H:%M")
            if len(columns) > 0:
                outage_details = {
                    "country": "India",
                    "start": self.today + "_" + start.strftime("%H-%M-%S"),
                    "end": self.today + "_" + end.strftime("%H-%M-%S"),
                    "duration_(hours)": int((end - start).total_seconds()/3600),
                    "event_category": "maintenance schedule",
                    # "REASON": columns[2].text,
                    "area_affected": {division: columns[3].text[:-1].split(",")}
                }
                res.append(outage_details)
        # time.sleep(3)
        self.save_json(res, provider)


    def run(self, provider):
        data = self.get_data()
        self.process(data, provider)
        print(f"Data is processed for {provider}.")


if __name__ == "__main__":
    file = ""
    file_list = file.split(".")
    date = file_list[-2]
    provider = file_list[2]
    date_list = date.split("-")
    year = date_list[0]
    month = date_list[1]
    process = Process_BSES(year, month, date, file)
    process.run(provider)
