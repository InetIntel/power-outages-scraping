from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup
import os


class Quetta:
    def __init__(self):
        self.url = "http://www.qesco.com.pk/Shutdown.aspx#google_vignette"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None

    def fetch(self):
        response = requests.get(self.url)
        if response.status_code != 200:
            print(f"Failed to access {self.url}")
            exit()
        else:
            return response

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        # headers = [th.get_text(strip=True) for th in soup.find_all("th")]
        rows = []
        for tr in soup.find_all("tr")[1:]:
            data = [td.get_text(strip=True) for td in tr.find_all("td")]
            date = str(datetime.strptime(data[2], "%d-%m-%Y").strftime("%Y-%m-%d")) + "_"
            times = data[3].split(",")
            start = times[0]+":00"
            end = times[1]+":00"
            start_time = datetime.strptime(start, "%H:%M")
            end_time = datetime.strptime(end, "%H:%M")
            tmp = {
                "country": "Pakistan",
                "start": date+start,
                "end": date+end,
                "duration_(hours)": int((end_time - start_time).total_seconds() / 3600),
                "event_category": data[4],
                "area_affected": {data[0]: data[1]}
            }
            rows.append(tmp)
            # rows.append(dict(zip(headers, data)))
        return rows

    def check_folder(self):
        self.folder_path = "./data/" + self.today
        os.makedirs(self.folder_path, exist_ok=True)

    def save_json(self, data):
        self.check_folder()
        file_path = os.path.join(self.folder_path, "quetta_shutdown_schedule_" + datetime.today().strftime("%Y-%m-%d") + ".json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)


    def scrape(self):
        response = self.fetch()
        data = self.parse(response)
        self.save_json(data)
        print("scraping is done for qesco")


if __name__ == "__main__":
    quetta = Quetta()
    quetta.scrape()

