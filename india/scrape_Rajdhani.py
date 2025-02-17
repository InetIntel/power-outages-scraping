import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import datetime
import time


class ScrapeRajdhani:

    def __init__(self, url, file_name):
        self.url = url
        self.file_name = file_name


    def check_folder(self):
        folder_path = "./data"
        os.makedirs(folder_path, exist_ok=True)

    def save_json(self, data):
        self.check_folder()
        file_path = os.path.join("./data", self.file_name + "outage_" + datetime.today().strftime("%Y-%m-%d") + ".json")
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
            today_date = datetime.today().strftime("%d-%m-%Y")
            select_date.select_by_value(today_date)
            time.sleep(2)
            dropdown = driver.find_elements(By.TAG_NAME, "select")
            select_division = Select(dropdown[1])
            select_division.select_by_visible_text("All Division")
            time.sleep(2)
            search_button = driver.find_element(By.XPATH, "//span[@class='lfr-btn-label' and text()='Search']")
            search_button.click()
            time.sleep(2)
            table_rows = driver.find_elements(By.XPATH, "//table[@class='table table-bordered table-striped']//tr")
            return table_rows
        except Exception as e:
            print("Today's outage schedule is not published.")


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
        self.save_json(res)

    def run(self):
        driver = self.fetch()
        data = self.selection(driver)
        if data:
            self.process(data)
        else:
            print("No outage data is found.")
        driver.quit()

urls = [('https://www.bsesdelhi.com/web/brpl/maintenance-outage-schedule', "BSES_Rajdhani_"),
        ("https://www.bsesdelhi.com/web/bypl/maintenance-outage-schedule", "BSES_Yamuna_")]
for url, file_name in urls:
    scrapeRajdhani = ScrapeRajdhani(url, file_name)
    scrapeRajdhani.run()
    time.sleep(2)




