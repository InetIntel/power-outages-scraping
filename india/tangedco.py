import os
from datetime import datetime
import requests
import urllib3


class Tangedco:

    def __init__(self, url):
        self.url = url
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None

    def check_folder(self):
        self.folder_path = "./data/" + self.today
        os.makedirs(self.folder_path, exist_ok=True)

    def fetch(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(self.url, verify=False)
        self.check_folder()
        if response.status_code == 200:
            path = os.path.join(self.folder_path, self.today + "_power_shutdown.html")
            with open(path, "w", encoding="utf-8") as file:
                file.write(response.text)
            print("HTML file saved successfully.")
        else:
            print("Failed to retrieve the webpage.")



url = "https://tneb.tnebnet.org/cpro/today.html"
tangedco = Tangedco(url)
tangedco.fetch()