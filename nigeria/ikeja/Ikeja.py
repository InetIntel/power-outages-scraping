import os
from nigeria.ikeja.process_Ikeja import Process_Ikeja
import requests
from datetime import datetime


class Ikeja:

    def __init__(self):
        self.url = "https://www.ikejaelectric.com/cnn/"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None
        self.year = str(datetime.now().year)
        self.month = str(datetime.now().month).zfill(2)


    def check_folder(self, type):
        self.folder_path = "./nigeria/ikeja/" + type + "/" + self.year + "/" + self.month
        os.makedirs(self.folder_path, exist_ok=True)

    def fetch(self):
        self.check_folder("raw")
        response = requests.get(self.url)
        if response.status_code == 200:
            file_name = "power_outages.NG.ikeja.raw." + self.today + ".html"
            file_path = os.path.join(self.folder_path, file_name)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(response.text)
                print("Raw file is download for Ikeja.")
                process = Process_Ikeja(self.year, self.month, self.today, self.folder_path + "/" + file_name)
                process.run()
        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

    def scrape(self):
        self.fetch()




if __name__ == "__main__":
    ikeja = Ikeja()
    ikeja.scrape()


