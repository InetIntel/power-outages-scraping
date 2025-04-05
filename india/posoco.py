from datetime import datetime
import requests
from bs4 import BeautifulSoup
import os


class Posoco:
    def __init__(self):
        self.url = "https://posoco.in/en/grid-disturbancesincidence/%e0%a4%97%e0%a5%8d%e0%a4%b0%e0%a4%bf%e0%a4%a1-%e0%a4%97%e0%a4%a1%e0%a4%bc%e0%a4%ac%e0%a4%a1%e0%a4%bc%e0%a5%80-%e0%a4%98%e0%a4%9f%e0%a4%a8%e0%a4%be%e0%a4%8f%e0%a4%82-2024-25/"
        self.month = datetime.today().strftime("%Y-%m")
        self.folder_path = None
        self.year = None
        self.month = None
        self.date = None


    def fetch(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            return response
        else:
            print(f"Failed to fetch the page: {self.url}")
            exit()


    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        tbody = soup.find('tbody')
        first_link = tbody.find('a', href=True)
        link = first_link['href']
        file_name = first_link.get_text(strip=True)
        file_name = file_name.split("_")
        self.year = "20" + file_name[-1]
        self.month = datetime.strptime(file_name[-2], "%B").strftime("%m")
        self.date = self.year + "-" + self.month
        return link


    def check_folder(self, type):
        self.folder_path = "./india/posoco/" + type + "/" + self.year + "/" + self.month
        os.makedirs(self.folder_path, exist_ok=True)


    def download(self, file_url):
        response = requests.get(file_url)
        self.check_folder("raw")
        if response.status_code == 200:
            filename = "power_outages.IND.posoco.raw." + self.date + ".pdf"
            file_path = os.path.join(self.folder_path, filename)
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"Download successful! File saved as {filename}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")


    def scrape(self):
        response = self.fetch()
        link = self.parse(response)
        self.download(link)
        print("scraping is done for posoco")


if __name__ == "__main__":
    posoco = Posoco()
    posoco.scrape()


