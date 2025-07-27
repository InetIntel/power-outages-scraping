import os
from datetime import datetime
import requests
import urllib3
from bs4 import BeautifulSoup

class Goa:
    def __init__(self):
        self.provider = "goa"
        self.country = "india"
        self.base_path = "/data"
        target_date = datetime.now()
        self.today = target_date.strftime("%Y-%m-%d")
        self.year = target_date.strftime("%Y")
        self.month = target_date.strftime("%m")
        self.url = "https://www.goaelectricity.gov.in/Goa_power_outage.aspx#"

    def create_folder(self, data_type):
        folder = os.path.join(self.base_path, self.country, self.provider, data_type, self.year, self.month)
        os.makedirs(folder, exist_ok=True)
        return folder

    def scrape(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        folder = self.create_folder("raw")

        try:
            response = requests.get(self.url, verify=False)
            soup = BeautifulSoup(response.text, "html.parser")
            planned_outage_h2 = soup.find("h2", string=lambda s: s and "Planned Power Outage" in s)
            content_area = None
            if planned_outage_h2:
                content_rt = planned_outage_h2.find_parent("div", class_="content_rt")
                if content_rt:
                    content_area = content_rt.find("div", class_="content_area")
            # Check if content_area is empty or only contains whitespace/newlines
            if not content_area or not content_area.get_text(strip=True):
                error_path = os.path.join(folder, f"404_{self.today}.txt")
                with open(error_path, "w", encoding="utf-8") as f:
                    f.write(f"No planned outage data found for {self.today}\n")
                print(f"No planned outage data found for {self.today}")
                return

            file_name = f"power_outages.IND.{self.provider}.raw.{self.today}.html"
            file_path = os.path.join(folder, file_name)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Saved raw outage table HTML: {file_path}")

        except Exception as e:
            error_path = os.path.join(folder, f"404_{self.today}.txt")
            with open(error_path, "w", encoding="utf-8") as f:
                f.write(f"Scrape failed for {self.today}: {type(e).__name__} - {str(e)}\n")
            print(f"Scrape failed: {type(e).__name__}: {e}")

if __name__ == "__main__":
    Goa().scrape()