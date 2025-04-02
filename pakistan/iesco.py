import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime



class Iesco:

    def __init__(self):
        self.page_url = "https://www.iesco.com.pk/index.php/customer-services/annual-maintenance-schedule"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None
        self.year = str(datetime.now().year)
        self.month = str(datetime.now().month).zfill(2)


    def check_folder(self, type):
        self.folder_path = "./pakistan/iesco/" + type + "/" + self.year + "/" + self.month
        os.makedirs(self.folder_path, exist_ok=True)

    def fetch(self):
        response = requests.get(self.page_url)
        if response.status_code != 200:
            print(f"Failed to access {self.page_url}")
            exit()
        else:
            return response


    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        links = [a["href"] for a in soup.find_all("a", href=True) if a.get_text(strip=True) == "Click To View"]
        full_links = [requests.compat.urljoin(self.page_url, link) for link in links]
        return full_links

    def download(self, file_url):
        response = requests.get(file_url)
        if response.status_code == 200:
            filename = "power_outages.PK.iesco.raw." + self.today + ".pdf"
            file_path = os.path.join(self.folder_path, filename)
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"Download successful! File saved as {filename}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")

    def scrape(self):
        response = self.fetch()
        links = self.parse(response)
        self.check_folder("raw")
        for link in links:
            self.download(link)
        print("scraping is done for iesco")


if __name__ == "__main__":
    iesco = Iesco()
    iesco.scrape()
