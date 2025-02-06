import csv
from datetime import datetime
from itertools import zip_longest
import requests
from bs4 import BeautifulSoup
from collections import defaultdict


class ScrapeWebpage:

    def __init__(self):
        self.url = "https://www.ikejaelectric.com/cnn/"

    def fetch(self):
        res = defaultdict(list)
        response = requests.get(self.url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            outages = soup.find_all('div', class_='col-md-4')
            for outage in outages:
                state_class = outage.find(class_=['post-category'])
                date_class = outage.find(class_=['post-date'])
                if state_class:
                    state = state_class.text
                    date = date_class.text
                    date = datetime.strptime(date, "%a, %d %b %Y").strftime("%Y-%m-%d")
                    if date not in res[state]:
                        res[state].append(date)
            return res
        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

    def scrape(self):
        data = self.fetch()
        self.process(data)

    def process(self, data):
        file_name = "outage_" + datetime.today().strftime("%Y-%m-%d") + ".csv"
        with open(file_name, mode="w", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())
            writer.writeheader()
            rows = zip_longest(*data.values(), fillvalue=None)
            for row in rows:
                writer.writerow(dict(zip(data.keys(), row)))

scrape_webpage = ScrapeWebpage()
scrape_webpage.scrape()


