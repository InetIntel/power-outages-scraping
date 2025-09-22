import json
import os
import pandas as pd
from datetime import datetime


class Process_tnpdcl:

    def __init__(self, year, month, today, file):
        self.year = year
        self.month = month
        self.today = today
        self.file = file

    def check_folder(self, type):
        self.folder_path = "./india/tnpdcl/" + type + "/" + self.year + "/" + self.month
        os.makedirs(self.folder_path, exist_ok=True)

    def save_json(self, data):
        self.check_folder("processed")
        file_path = os.path.join(self.folder_path,
                                 "power_outages.IND.tnpdcl.processed." + self.today + ".json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def read_file(self):
        df = pd.read_excel(self.file, engine="openpyxl", header=None)[2:]
        outage = []
        for i in range(len(df)):
            row = df.iloc[i]
            date = datetime.strptime(row[0], "%d-%m-%Y").strftime("%Y-%m-%d")
            start = datetime.strptime(row[6], "%H:%M")
            end = datetime.strptime(row[7], "%H:%M")
            data = {
                "country": "India",
                "start": date + "_" + start.strftime("%H-%M-%S"),
                "end": date + "_" + end.strftime("%H-%M-%S"),
                "duration_(hours)": int((end - start).total_seconds() / 3600),
                "event_category": "planned power shutdown",
                "area_affected": {row[1]:row[4].split(",")}
            }
            outage.append(data)
        return outage

    def run(self):
        data = self.read_file()
        self.save_json(data)
        print("Outage data is processed for tnpdcl.")


if __name__ == "__main__":
    file = ""
    file_list = file.split(".")
    date = file_list[-2]
    date_list = date.split("-")
    year = date_list[0]
    month = date_list[1]
    process = Process_tnpdcl(year, month, date, file)
    process.run()
