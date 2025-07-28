import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime


class Posoco:
    def __init__(self):
        self.url = "https://posoco.in/en/grid-disturbancesincidence/%e0%a4%97%e0%a5%8d%e0%a4%b0%e0%a4%bf%e0%a4%a1-%e0%a4%97%e0%a4%a1%e0%a4%bc%e0%a4%ac%e0%a4%a1%e0%a4%bc%e0%a5%80-%e0%a4%98%e0%a4%9f%e0%a4%a8%e0%a4%be%e0%a4%8f%e0%a4%82-2024-25/"
        self.folder_path = None
        self.year = None
        self.month = None
        self.date = None

    def fetch(self):
        response = requests.get(self.url)
        if response.status_code != 200:
            print(f"Failed to fetch the page: {self.url}")
            exit(1)
        return response

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        tbody = soup.find("tbody")
        if not tbody:
            print("No table body found.")
            exit(1)

        first_link = tbody.find("a", href=True)
        if not first_link:
            print("No PDF link found.")
            exit(1)

        link = first_link["href"]
        file_name = first_link.get_text(strip=True).split("_")
        try:
            self.year = "20" + file_name[-1]
            self.month = datetime.strptime(file_name[-2], "%B").strftime("%m")
        except Exception as e:
            print(f"Failed to parse filename metadata: {e}")
            exit(1)

        self.date = f"{self.year}-{self.month}"
        return link

    def check_folder(self, type_):
        self.folder_path = f"/data/india/posoco/{type_}/{self.year}/{self.month}"
        os.makedirs(self.folder_path, exist_ok=True)

    def download(self, file_url):
        response = requests.get(file_url)
        if response.status_code == 200:
            self.check_folder("raw")
            filename = f"power_outages.IND.posoco.raw.{self.date}.pdf"
            file_path = os.path.join(self.folder_path, filename)
            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"Saved: {file_path}")
        else:
            print(f"Failed to download file: {file_url} (status: {response.status_code})")

    def scrape(self):
        response = self.fetch()
        file_url = self.parse(response)
        self.download(file_url)
        print("Scraping complete for POSOCO.")


if __name__ == "__main__":
    posoco = Posoco()
    posoco.scrape()
