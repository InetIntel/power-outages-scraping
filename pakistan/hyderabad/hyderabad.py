import os
from datetime import datetime
import requests
import urllib3
from bs4 import BeautifulSoup


class Hyderabad:

    def __init__(self):
        self.url = "http://www.hesco.gov.pk/shutdownschedule.asp"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None
        self.year = str(datetime.now().year)
        self.month = str(datetime.now().month).zfill(2)

    def check_folder(self, type):
        self.folder_path = "./pakistan/hyderabad/" + type + "/" + self.year + "/" + self.month
        os.makedirs(self.folder_path, exist_ok=True)

    def scrape(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.check_folder("raw")
        response = requests.get(self.url, verify=False)
        # soup = BeautifulSoup(response.content, 'html.parser')
        file_name = "power_outages.PK.hyderabad.raw." + self.today + ".html"
        # div_element = soup.find('table', class_='table table-bordered table-striped table-responsive sschedule')
        # div_html = str(div_element)
        html_filename = os.path.join(self.folder_path, file_name)
        with open(html_filename, 'w', encoding='utf-8') as file:
            file.write(response.text)
            print("scraping is done for hyderabad")



if __name__ == "__main__":
    hyderabad = Hyderabad()
    hyderabad.scrape()