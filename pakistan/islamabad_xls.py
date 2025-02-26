import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime



class IslamabadXls:

    def __init__(self, url):
        self.page_url = url
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None


    def check_folder(self):
        self.folder_path = "./data/" + self.today
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
        full_links = [requests.compat.urljoin(url, link) for link in links]
        return full_links

    def download(self, file_url):
        response = requests.get(file_url)
        if response.status_code == 200:
            filename = os.path.basename(file_url)
            file_path = os.path.join(self.folder_path, filename)
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"Download successful! File saved as {filename}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")

    def scrape(self,):
        response = self.fetch()
        links = self.parse(response)
        self.check_folder()
        for link in links:
            self.download(link)


url = "https://www.iesco.com.pk/index.php/customer-services/annual-maintenance-schedule"
islamabadXls = IslamabadXls(url)
islamabadXls.scrape()
