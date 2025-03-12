import os
from datetime import datetime
import requests
import urllib3


class Tangedco:

    def __init__(self):
        self.url = "https://tneb.tnebnet.org/cpro/today.html"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None

    def check_folder(self):
        self.folder_path = "./data/" + self.today
        os.makedirs(self.folder_path, exist_ok=True)

    def scrape(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(self.url, verify=False)
        self.check_folder()
        if response.status_code == 200:
            path = os.path.join(self.folder_path, self.today + "_power_shutdown.html")
            with open(path, "w", encoding="utf-8") as file:
                file.write(response.text)
            print("scraping is done for tnebnet")
        else:
            print("Failed to retrieve the webpage.")



if __name__ == "__main__":
    tnebnet = Tangedco()
    tnebnet.scrape()