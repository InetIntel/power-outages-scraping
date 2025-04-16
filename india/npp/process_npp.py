import json
import os
import pandas as pd
from datetime import datetime


class Process_Npp:

    def __init__(self, year, month, today, file, report_name):
        self.year = year
        self.month = month
        self.today = today
        self.file = file
        self.report_name = report_name


    def check_folder(self, type):
        # folder to save the processed data file
        self.folder_path = "./india/npp/" + type + "/" + self.year + "/" + self.month
        os.makedirs(self.folder_path, exist_ok=True)

    def save_json(self, data):
        self.check_folder("processed")
        file_name = "power_outages.IND." + ".processed." + self.today + "." + self.report_name + ".json"
        file_path = os.path.join(self.folder_path, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
            print("Outage data is saved for npp.")

    def read_file(self):
        df = pd.read_excel(self.file, engine="xlrd", header=None)[3:]
        outage = []
        for i in range(len(df)):
            row = df.iloc[i]
            if pd.isnull(row[9]) or row[9] == "10" or row[9] == "Reasons/Present Status":
                continue
            start_date_time = row[7].split(" ")
            start_date = start_date_time[0]
            start_date = datetime.strptime(start_date, "%d/%m/%Y").strftime("%Y-%m-%d")
            start_time = datetime.strptime(start_date_time[1], "%H:%M")
            data = {
                "country": "India",
                "start": start_date + "_" + start_time.strftime("%H-%M-%S"),
            }
            if not pd.isnull(row[8]):
                end_date_time = row[8].split(" ")
                end_date = end_date_time[0]
                end_date = datetime.strptime(end_date, "%d/%m/%Y").strftime("%Y-%m-%d")
                end_time = datetime.strptime(end_date_time[1], "%H:%M")
                data["end"] = end_date + "_" + end_time.strftime("%H-%M-%S")
                fmt = "%d/%m/%Y %H:%M"
                start = datetime.strptime(row[7], fmt)
                end = datetime.strptime(row[8], fmt)
                data["duration_(hours)"] = round((end - start).total_seconds() / 3600, 2)
            data["event_category"] = row[9]
            data["area_affected"] = {row[0]: row[1]}
            outage.append(data)
        return outage

    def run(self):
        data = self.read_file()
        self.save_json(data)


if __name__ == "__main__":
    # relative path to a file to be processed
    file = "raw/2025/04/power_outages.IND.npp.raw.2025-04-08.dgr11-2025-04-08.xls"
    file_list = file.split(".")
    report_name = file_list[-2]
    date = file_list[-3]
    data_list = date.split("-")
    year = data_list[0]
    month = data_list[1]
    process = Process_Npp(year, month, date, file, report_name)
    process.run()