import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import datetime
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ScrapeRajdhani:

    def __init__(self):
        self.day = datetime.today().strftime("%Y-%m-%d")
        self.today = datetime.today().strftime("%d-%m-%Y")
        self.folder_path = None
        self.urls = [('https://www.bsesdelhi.com/web/brpl/maintenance-outage-schedule', "BSES_Rajdhani_"),
        ("https://www.bsesdelhi.com/web/bypl/maintenance-outage-schedule", "BSES_Yamuna_")]


    def check_folder(self):
        self.folder_path = "./data/" + self.day
        os.makedirs(self.folder_path, exist_ok=True)

    def save_json(self, data, file_name):
        self.check_folder()
        file_path = os.path.join(self.folder_path, file_name + "outage_" + self.today + ".json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)


    def fetch(self, url):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(2)
        return driver

    def selection(self, driver, file_name):
        dropdown = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "select"))
        )
        select_date = Select(dropdown)
        try:
            select_date.select_by_value(self.today)
            time.sleep(2)
            dropdown = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "select"))
            )
            select_division = Select(dropdown[1])
            select_division.select_by_visible_text("All Division")
            search_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//span[@class='lfr-btn-label' and text()='Search']"))
            )
            search_button.click()
            table_rows = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//table[@class='table table-bordered table-striped']//tr"))
            )
            return table_rows
        except Exception as e:
            print(f"Outage schedule is not published for {file_name[:-1]} on {self.today}")


    def process(self, table_rows, file_name):
        res = []
        for row in table_rows[2:]:
            columns = row.find_elements(By.TAG_NAME, "td")
            division = columns[0].text
            hours = columns[1].text.split("-")
            start = datetime.strptime(hours[0], "%H:%M")
            end = datetime.strptime(hours[1], "%H:%M")
            if len(columns) > 0:
                outage_details = {
                    "country": "India",
                    "start": self.day + "_" + start.strftime("%H-%M-%S"),
                    "end": self.day + "_" + end.strftime("%H-%M-%S"),
                    "duration_(hours)": int((end - start).total_seconds()/3600),
                    "event_category": "maintenance schedule",
                    # "REASON": columns[2].text,
                    "area_affected": {division: columns[3].text[:-1].split(",")}
                }
                res.append(outage_details)
        time.sleep(3)
        self.save_json(res, file_name)
        print(f"Data is saved for {self.today}")

    def scrape(self):
        for url, file_name in self.urls:
            driver = self.fetch(url)
            data = self.selection(driver, file_name)
            if data:
                self.process(data, file_name)
            else:
                print(f"No outage data is found for {file_name[:-1]}.")
            driver.quit()
            time.sleep(2)


if __name__ == "__main__":
    bsesdelhi = ScrapeRajdhani()
    bsesdelhi.scrape()





