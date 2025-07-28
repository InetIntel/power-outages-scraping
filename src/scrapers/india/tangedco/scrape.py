import os
from datetime import datetime
import requests
import urllib3

class TangedcoScraper:
    def __init__(self):
        self.url = "https://tneb.tnebnet.org/cpro/today.html"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.year = datetime.today().strftime("%Y")
        self.month = datetime.today().strftime("%m")
        self.folder_path = f"/data/india/tangedco/raw/{self.year}/{self.month}"
        os.makedirs(self.folder_path, exist_ok=True)

    def scrape(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        try:
            response = requests.get(self.url, verify=False, timeout=10)
            response.raise_for_status()

            filename = f"power_outages.IND.tangedco.raw.{self.today}.html"
            file_path = os.path.join(self.folder_path, filename)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)

            print(f"Saved: {file_path}")

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")

if __name__ == "__main__":
    TangedcoScraper().scrape()
