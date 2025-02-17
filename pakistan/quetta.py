from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup
import os


class Quetta:
    def __init__(self, url):
        self.url = url

    def fetch(self):
        response = requests.get(self.url)
        if response.status_code != 200:
            print(f"Failed to access {self.url}")
            exit()
        else:
            return response

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        headers = [th.get_text(strip=True) for th in soup.find_all("th")]
        rows = []
        for tr in soup.find_all("tr")[1:]:
            data = [td.get_text(strip=True) for td in tr.find_all("td")]
            rows.append(dict(zip(headers, data)))
        return rows

    def check_folder(self):
        folder_path = "./data"
        os.makedirs(folder_path, exist_ok=True)

    def save_json(self, data):
        self.check_folder()
        file_path = os.path.join("./data", "quetta_shutdown_schedule_" + datetime.today().strftime("%Y-%m-%d") + ".json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)


    def run(self):
        response = self.fetch()
        data = self.parse(response)
        self.save_json(data)

url = "http://www.qesco.com.pk/Shutdown.aspx#google_vignette"
quetta = Quetta(url)
quetta.run()

