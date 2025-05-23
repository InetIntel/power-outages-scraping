import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from india.tata.process_tata import Process_tata

class Tata:

    def __init__(self):
        self.url = "https://customerportal.tatapower.com/TPCD/OuterOutage.aspx#"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.year = str(datetime.now().year)
        self.month = str(datetime.now().month).zfill(2)

    def check_folder(self, type):
        self.folder_path = "./india/tata/" + type + "/" + self.year + "/" + self.month
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
        self.check_folder("raw")
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.ID, "table1")))
        headers = driver.find_elements(By.XPATH, "//thead//th")
        # titles = [header.text for header in headers]
        response = driver.page_source
        file_name = "power_outages.IND.tata.raw." + self.today + ".html"
        file_path = os.path.join(self.folder_path, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(response)
            print("Raw file is download for TATA.")
        process = Process_tata(self.year, self.month, self.today, self.folder_path + "/" + file_name)
        process.run()
        # rows = driver.find_elements(By.XPATH, "//tbody[@id='tbodyid']/tr")
        # data = []
        # for row in rows:
        #     cols = row.find_elements(By.TAG_NAME, "td")
        #     start_time = datetime.strptime(cols[3].text, "%B %d, %Y %H:%M")
        #     end_time = datetime.strptime(cols[4].text, "%B %d, %Y %H:%M")
        #     row_data = {
        #         "country": "India",
        #         "start": start_time.strftime("%Y-%m-%d_%H-%M-%S"),
        #         "end": end_time.strftime("%Y-%m-%d_%H-%M-%S"),
        #         "duration_(hours)": int((end_time - start_time).total_seconds() / 3600),
        #         "event_category": cols[2].text,
        #         # "REASON": columns[2].text,
        #         "area_affected": {cols[0].text: cols[1].text.split(",")}
        #     }
        #     # for i in range(len(cols)):
        #     #     row_data[titles[i]] = cols[i].text
        #     data.append(row_data)
        # return data

    def save_json(self, data):
        self.check_folder("processed")
        file_name = "tatapower"
        file_path = os.path.join(self.folder_path, file_name + "_outage_" + self.today + ".json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
            print("scraping is done for tatapower")

    def scrape(self):
        driver = self.fetch()
        outage_number = self.check_outage(driver)
        if outage_number != 0:
            self.process(driver)
            # data = self.process(driver)
            # self.save_json(data)
        else:
            print("No outage data from Tata power.")
        driver.quit()



if __name__ == "__main__":
    tatapower = Tata()
    tatapower.scrape()

