import os
from datetime import datetime
import requests
import urllib3
from bs4 import BeautifulSoup


class Hyderabad:

    def __init__(self, url):
        self.url = url
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None

    def check_folder(self):
        self.folder_path = "./data/" + self.today
        os.makedirs(self.folder_path, exist_ok=True)

    def fetch(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.check_folder()
        response = requests.get(self.url, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        div_element = soup.find('table', class_='table table-bordered table-striped table-responsive sschedule')
        div_html = str(div_element)
        html_filename = os.path.join(self.folder_path, self.today + "_shutdown_schedule.html")
        with open(html_filename, 'w', encoding='utf-8') as file:
            file.write(div_html)
            print("HTML file saved successfully.")



url = "http://www.hesco.gov.pk/shutdownschedule.asp"
hyderabad = Hyderabad(url)
hyderabad.fetch()