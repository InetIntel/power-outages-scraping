import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

class Tata:

    def __init__(self):
        self.url = "https://customerportal.tatapower.com/TPCD/OuterOutage.aspx#"
        self.today = datetime.today().strftime("%Y-%m-%d")

    def check_folder(self):
        self.folder_path = "./data/" + self.today
        os.makedirs(self.folder_path, exist_ok=True)

    def fetch(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=options)
        driver.get(self.url)
        WebDriverWait(driver, 20).until(lambda d: d.execute_script("return document.readyState") == "complete")
        wait = WebDriverWait(driver, 20)
        wait.until(EC.invisibility_of_element_located((By.ID, "page_loader")))
        element = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@tabindex='1' and @aria-label='Click to List']")))
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        element.click()
        WebDriverWait(driver, 20).until(lambda d: d.execute_script("return document.readyState") == "complete")
        wait = WebDriverWait(driver, 20)
        wait.until(EC.invisibility_of_element_located((By.ID, "page_loader")))
        return driver

    def check_outage(self, driver):
        element = driver.find_element(By.ID, "totalPOutageSpan")
        outage_number = element.text
        return outage_number

    def process(self, driver):
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.ID, "table1")))
        headers = driver.find_elements(By.XPATH, "//thead//th")
        titles = [header.text for header in headers]
        rows = driver.find_elements(By.XPATH, "//tbody[@id='tbodyid']/tr")
        data = []
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            row_data = dict()
            for i in range(len(cols)):
                row_data[titles[i]] = cols[i].text
            data.append(row_data)
        return data

    def save_json(self, data):
        self.check_folder()
        file_name = "tatapower"
        file_path = os.path.join(self.folder_path, file_name + "_outage_" + self.today + ".json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
            print("scraping is done for tatapower")

    def scrape(self):
        driver = self.fetch()
        outage_number = self.check_outage(driver)
        if outage_number != 0:
            data = self.process(driver)
            self.save_json(data)
        else:
            print("No outage data from Tata power.")
        driver.quit()


if __name__ == "__main__":
    tatapower = Tata()
    tatapower.scrape()

