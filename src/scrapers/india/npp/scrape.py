import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

class NppScraper:
    def __init__(self):
        self.page_url = "https://npp.gov.in/publishedReports"
        self.base_url = "https://npp.gov.in"
        self.reports = [
            "Daily Outage Report (Coal,Lignite and Nuclear)",
            "Daily Outage Report (Thermal/Nuclear Units) only for 500M"
        ]
        self.today = None
        self.year = None
        self.month = None
        self.folder_path = None

    def check_folder(self, data_type):
        self.folder_path = os.path.join("/data", "india", "npp", data_type, self.year, self.month)
        os.makedirs(self.folder_path, exist_ok=True)

    def fetch(self):
        res = requests.get(self.page_url)
        if res.status_code != 200:
            raise Exception(f"Failed to fetch {self.page_url}")
        return res

    def parse_date_from_page(self, soup):
        # Extract latest date from page
        h3_tags = soup.find_all('h3', class_='mb-0')
        if not h3_tags or len(h3_tags) < 2:
            raise Exception("Date header not found on page.")
        raw_date = h3_tags[1].get_text(strip=True)[-11:-1]
        dd, mm, yyyy = raw_date.split("-")
        self.year, self.month, self.today = yyyy, mm, f"{yyyy}-{mm}-{dd}"

    def parse_report_link(self, soup, report_title):
        items = soup.find_all('li', class_='d-flex justify-content-between align-items-center')
        for item in items:
            title_tag = item.find('p', class_='mp01')
            if title_tag and report_title in title_tag.get_text(strip=True):
                for link in item.find_all('a', href=True):
                    if link['href'].endswith(".xls"):
                        return self.base_url + link['href']
        return None

    def download(self, report_title, file_url):
        response = requests.get(file_url)
        if response.status_code != 200:
            print(f"Failed to download {file_url}")
            return

        original_name = os.path.basename(file_url)
        filename = f"power_outages.IND.npp.raw.{self.today}.{original_name}"
        file_path = os.path.join(self.folder_path, filename)

        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"Saved: {file_path}")

    def scrape(self):
        try:
            response = self.fetch()
            soup = BeautifulSoup(response.text, 'html.parser')
            self.parse_date_from_page(soup)

            for report in self.reports:
                file_url = self.parse_report_link(soup, report)
                if file_url:
                    self.check_folder("raw")
                    self.download(report, file_url)
                else:
                    print(f"⚠️ Report not found: {report}")

            print("Scraping complete for NPP.")

        except Exception as e:
            print(f"Error during scraping: {type(e).__name__}: {e}")

if __name__ == "__main__":
    NppScraper().scrape()
