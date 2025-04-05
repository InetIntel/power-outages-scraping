from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup
import os
from pakistan.process_quetta import Process_quetta


class Quetta:
    def __init__(self):
        self.url = "http://www.qesco.com.pk/Shutdown.aspx#google_vignette"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None
        self.year = str(datetime.now().year)
        self.month = str(datetime.now().month).zfill(2)


    def check_folder(self, type):
        self.folder_path = "./pakistan/quetta/" + type + "/" + self.year + "/" + self.month
        os.makedirs(self.folder_path, exist_ok=True)


    def fetch(self):
        response = requests.get(self.url)
        if response.status_code != 200:
            print(f"Failed to access {self.url}")
            exit()
        else:
            return response


    def scrape(self):
        response = self.fetch()
        self.check_folder("raw")
        file_name = "power_outages.PK.quetta.raw." + self.today + ".html"
        file_path = os.path.join(self.folder_path, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(response.text)
            print("Raw file is download for quetta.")
        process = Process_quetta(self.year, self.month, self.today, self.folder_path + "/" + file_name)
        process.run()


if __name__ == "__main__":
    quetta = Quetta()
    quetta.scrape()

