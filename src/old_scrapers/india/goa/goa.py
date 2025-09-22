import os
from datetime import datetime
import requests
import urllib3
from india.goa.process_GOA import Process_GOA


class Goa:

    def __init__(self):
        self.url = "https://www.goaelectricity.gov.in/Goa_power_outage.aspx#"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None
        self.year = str(datetime.now().year)
        self.month = str(datetime.now().month).zfill(2)

    def check_folder(self, type):
        self.folder_path = "./india/goa/" + type + "/" + self.year + "/" + self.month
        os.makedirs(self.folder_path, exist_ok=True)

    def scrape(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.check_folder("raw")

        response = requests.get(self.url, verify=False)
        file_name = "power_outages.IND.goa.raw." + self.today + ".html"
        file_path = os.path.join(self.folder_path, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(response.text)
            print("Raw file is download for GOA.")
        process = Process_GOA(self.year, self.month, self.today, self.folder_path + "/" + file_name)
        process.run()



if __name__ == "__main__":
    goa = Goa()
    goa.scrape()