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
        last_two_reports = report_rows[-1:]
        res = []
        for row in last_two_reports:
            links = row.find_all('a', href=True)
            for link in links:
                href = self.base_url + link.get('href')
                text = link.get_text(strip=True)
                res.append((href, text))
        return res

    def check_folder(self):
        self.folder_path = "./data/" + self.today
        os.makedirs(self.folder_path, exist_ok=True)

    def download(self, data):
        self.check_folder()
        for file_url, filename in data:
            response = requests.get(file_url)
            if response.status_code == 200:
                filename += ".pdf"
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



# fesco = Fesco()
# fesco.scrape()
