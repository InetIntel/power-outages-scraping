import os

import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime


class ScrapeWebpage:

    def __init__(self):
        self.url = "https://www.ikejaelectric.com/cnn/"

    def fetch(self):
        res = list()
        response = requests.get(self.url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            outages = soup.find_all('div', class_='col-md-4')
            for outage in outages:
                state_class = outage.find(class_=['post-category'])
                date_class = outage.find(class_=['post-date'])
                tmp = dict()
                if state_class:
                    tmp["STATE"] = state_class.text
                    date = date_class.text
                    date = datetime.strptime(date, "%a, %d %b %Y").strftime("%Y-%m-%d")
                    tmp["Date"] = date
                    info = outage.find('h3', class_='post-title')
                    info = info.get_text(separator=" ", strip=True).split(" ")
                    i = 0
                    while i < len(info):
                        key = info[i].strip()[:-1]
                        tmp[key] = ""
                        text = ""
                        i += 1
                        while i < len(info) and ":" not in info[i]:
                            text += info[i].strip() + " "
                            i += 1
                        tmp[key] = text.strip()
                res.append(tmp)
            return res
        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

    def scrape(self):
        data = self.fetch()
        self.save_json(data)

    def save_json(self, data):
        file_path = os.path.join("./nigeria/data", "outage_" + datetime.today().strftime("%Y-%m-%d") + ".json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

folder_path = "./nigeria/data"
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
scrape_webpage = ScrapeWebpage()
scrape_webpage.scrape()


