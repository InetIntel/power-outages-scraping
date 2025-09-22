import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup


class Fesco:

    def __init__(self):
        self.url = "http://mis.fesco.com.pk/fescoweb/old.fesco.com.pk/News/shutdown_Choice.asp"
        self.base_url = "http://mis.fesco.com.pk/fescoweb/old.fesco.com.pk/News/"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None
        self.year = str(datetime.now().year)
        self.month = str(datetime.now().month).zfill(2)

    def fetch(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            return response
        else:
            print(f"Failed to fetch the page: {self.url}")
            exit()

    def parse(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', id='table1')
        rows = table.find_all('tr')
        report_rows = [row for row in rows if row.find('a', href=True)]
        reports = report_rows[-1:]
        res = []
        for row in reports:
            links = row.find_all('a', href=True)
            for link in links:
                href = self.base_url + link.get('href')
                text = link.get_text(strip=True)
                res.append((href, text))
        return res

    def check_folder(self, type):
        self.folder_path = "./pakistan/fesco/" + type + "/" + self.year + "/" + self.month
        os.makedirs(self.folder_path, exist_ok=True)

    def download(self, data):
        self.check_folder("raw")
        for file_url, original_file_name in data:
            response = requests.get(file_url)
            if response.status_code == 200:
                filename = "power_outages.PK.fesco.raw." + self.today + "." + original_file_name + ".pdf"
                file_path = os.path.join(self.folder_path, filename)
                with open(file_path, "wb") as file:
                    file.write(response.content)
                print(f"Download successful! File saved as {filename}")
            else:
                print(f"Failed to download file. Status code: {response.status_code}")

    def scrape(self):
        response = self.fetch()
        data = self.parse(response)
        self.download(data)
        print("scraping is done for fesco")


if __name__ == "__main__":
    fesco = Fesco()
    fesco.scrape()
