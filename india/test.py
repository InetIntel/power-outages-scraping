import json
import os

from selenium.webdriver.support.ui import Select
from datetime import datetime, timedelta
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ScrapeRajdhani:

    def __init__(self, url, file_name, day):
        self.url = url
        self.file_name = file_name
        self.day = day
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None


    def check_folder(self):
        self.folder_path = "./test/" + self.today
        os.makedirs(self.folder_path, exist_ok=True)

    def save_json(self, data):
        self.check_folder()
        file_path = os.path.join(self.folder_path, self.file_name + "outage_" + self.day + ".json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)


    def fetch(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=options)
        driver.get(self.url)
        time.sleep(2)
        return driver

    def selection(self, driver):
        dropdown = driver.find_element(By.TAG_NAME, "select")
        select_date = Select(dropdown)
        try:
            select_date.select_by_value(self.day)
            time.sleep(2)
            dropdown = driver.find_elements(By.TAG_NAME, "select")
            select_division = Select(dropdown[1])
            select_division.select_by_visible_text("All Division")
            time.sleep(2)
            search_button = driver.find_element(By.XPATH, "//span[@class='lfr-btn-label' and text()='Search']")
            search_button.click()
            time.sleep(5)
            table_rows = driver.find_elements(By.XPATH, "//table[@class='table table-bordered table-striped']//tr")
            return table_rows
        except Exception as e:
            print(f"Outage schedule is not published for {self.file_name[:-1]} on {self.day}")


    def process(self, table_rows):
        res = []
        for row in table_rows[1:]:
            columns = row.find_elements(By.TAG_NAME, "td")
            if len(columns) > 0:
                outage_details = {
                    "DIVISION": columns[0].text,
                    "TIME(HRS)": columns[1].text,
                    "REASON": columns[2].text,
                    "AREA": columns[3].text
                }
                res.append(outage_details)
        time.sleep(2)
        self.save_json(res)
        print(f"Data is saved for {self.day}")

    def run(self):
        driver = self.fetch()
        data = self.selection(driver)
        if data:
            self.process(data)
        else:
            print(f"No outage data is found for {self.file_name[:-1]} on {self.day}.")
        driver.quit()

url, file_name = ('https://www.bsesdelhi.com/web/brpl/maintenance-outage-schedule', "BSES_Rajdhani_")
days = ["20-02-2025","21-02-2025","22-02-2025","23-02-2025","24-02-2025","25-02-2025","26-02-2025"]
# days = ["21-02-2025"]

for day in days:
    scrapeRajdhani = ScrapeRajdhani(url, file_name, day)
    scrapeRajdhani.run()
    time.sleep(2)




