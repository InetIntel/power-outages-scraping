import requests
from bs4 import BeautifulSoup
import os



class ScrapeXls:

    def __init__(self):
        self.page_url = "https://npp.gov.in/publishedReports"
        self.base_url = "https://npp.gov.in"


    def check_folder(self):
        folder_path = "./data"
        os.makedirs(folder_path, exist_ok=True)


    def fetch(self):
        response = requests.get(self.page_url)
        if response.status_code != 200:
            print(f"Failed to access {self.page_url}")
            exit()
        else:
            return response

    def parse(self, response, target_text):
        soup = BeautifulSoup(response.text, "html.parser")
        file_link = None
        for td_tag in soup.find_all("td"):
            if target_text in td_tag.text.strip():
                next_td = td_tag.find_next("td")
                if next_td:
                    for a_tag in next_td.find_all("a", href=True):
                        file_url = a_tag["href"]
                        if file_url.endswith(".xls"):
                            file_link = file_url
                            break
        if not file_link:
            print("No matching outage report found on the page.")
            exit()
        file_url = self.base_url + file_link
        return file_url

    def download(self, file_url):
        response = requests.get(file_url)
        if response.status_code == 200:
            filename = os.path.basename(file_url)
            file_path = os.path.join("./data", filename)
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"Download successful! File saved as {filename}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")

    def scrape(self, report_name):
        response = self.fetch()
        file_url = self.parse(response, report_name)
        self.check_folder()
        self.download(file_url)

scrape_xls = ScrapeXls()
reports = ["10.Daily Outage Report", "11. Daily Outage Report"]
for report in reports:
    scrape_xls.scrape(report)
