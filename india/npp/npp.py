import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
from india.npp.process_npp import Process_Npp


class Npp:

    def __init__(self):
        self.page_url = "https://npp.gov.in/publishedReports"
        self.base_url = "https://npp.gov.in"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None
        self.reports = [("Daily Outage Report (Coal,Lignite and Nuclear)", "1"),
                        ("Daily Outage Report (Thermal/Nuclear Units) only for 500M", "2")]
        self.year = None
        self.month = None
        self.today = None

    def check_folder(self, type):
        self.folder_path = "./india/npp/" + type + "/" + self.year + "/" + self.month
        os.makedirs(self.folder_path, exist_ok=True)


    def fetch(self):

        response = requests.get(self.page_url)
        if response.status_code != 200:
            print(f"Failed to access {self.page_url}")
            exit()
        else:
            return response


    def parse(self, response, target_text):
        soup = BeautifulSoup(response.text, 'html.parser')
        daily_report = soup.find_all('h3', class_='mb-0')
        daily_report = daily_report[1].get_text(strip=True)
        date = daily_report[-11:-1]
        date = date.split("-")
        self.year = date[2]
        self.month = date[1]
        self.today = self.year + "-" + self.month + "-" + date[0]


        list_items = soup.find_all('li', class_='d-flex justify-content-between align-items-center')
        file_url = None
        for item in list_items:
            title_tag = item.find('p', class_='mp01')
            if title_tag:
                title = title_tag.get_text(strip=True)
                if target_text in title:
                    links = item.find_all('a', href=True)
                    for link in links:
                        href = link['href']
                        if href.endswith('.xls'):
                            file_url = href
                    break
        return file_url


    def download(self, file_url, index):
        file_url = self.base_url + file_url
        original_file_name = file_url.split("/")[-1]
        response = requests.get(file_url)
        if response.status_code == 200:
            filename = "power_outages.IND.npp.raw." + self.today + "_" + index + "." + original_file_name
            file_path = os.path.join(self.folder_path, filename)
            with open(file_path, "wb") as file:
                file.write(response.content)
                process = Process_Npp(self.year, self.month, self.today, file_path, index)
                process.run()
            print(f"Download successful! File saved as {filename}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")

    def scrape(self):
        for report, index in self.reports:
            response = self.fetch()
            file_url = self.parse(response, report)
            if file_url is None:
                print(f"{report} is not found")
            else:
                self.check_folder("raw")
                self.download(file_url, index)
        print("scraping is done for npp")

if __name__ == "__main__":
    npp = Npp()
    npp.scrape()
