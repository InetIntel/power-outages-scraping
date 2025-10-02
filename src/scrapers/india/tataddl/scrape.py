# import os
# from datetime import datetime
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
import os
import time
import traceback
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

#import json
#from india.tata.process_tata import Process_tata

class Tataddl:

    def __init__(self):
        self.provider = "tataddl"
        self.country = "india"
        self.base_path = "/data"
        self.today = datetime.now()
        self.today_iso = self.today.strftime("%Y-%m-%d")
        self.year = self.today.strftime("%Y")
        self.month = self.today.strftime("%m")
        self.url = "https://tatapower-ddl.com/scheduleoutage/119/customers/scheduled-outage"

    def create_folder(self, data_type):
        folder_path = os.path.join(self.base_path, self.country, self.provider, data_type, self.year, self.month)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def get_chrome_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.binary_location = "/usr/bin/chromium-browser"
        service = Service("/usr/bin/chromedriver")
        service = Service("/usr/bin/chromedriver")
        return webdriver.Chrome(options=options)

    def fetch(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=options)
        driver.get(self.url)
        WebDriverWait(driver, 20).until(lambda d: d.execute_script("return document.readyState") == "complete")
        wait = WebDriverWait(driver, 20)
        # Wait for dropdown to be present
        wait.until(EC.presence_of_element_located((By.ID, "ddlYear")))
        select = Select(driver.find_element(By.ID, "ddlYear"))
        select.select_by_index(1)
        # Wait for table to appear
        wait.until(EC.presence_of_element_located((By.ID, "ddlYear")))
        return driver

    def scrape(self):
        raw_folder = self.create_folder("raw")
        try:
            driver = self.get_chrome_driver()
            driver.get(self.url)
            WebDriverWait(driver, 20).until(lambda d: d.execute_script("return document.readyState") == "complete")
            wait = WebDriverWait(driver, 20)
            # Wait for dropdown to be present
            wait.until(EC.presence_of_element_located((By.ID, "ddlYear")))
            select = Select(driver.find_element(By.ID, "ddlYear"))
            select.select_by_index(1)
            # Wait for table to appear
            wait.until(EC.presence_of_element_located((By.ID, "ddlYear")))
            html = driver.page_source
            file_path = os.path.join(raw_folder, f"power_outages.IND.{self.provider}.raw.{self.today_iso}.html")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Saved raw outage HTML: {file_path}")
        except Exception as e:
            err_type = type(e).__name__
            err_msg = str(e) or "No additional error message."
            full_trace = traceback.format_exc()

            print(f"Scraping failed: {err_type}: {err_msg}")
            print(full_trace)

            error_file = os.path.join(raw_folder, f"404_{self.today_iso}.txt")
            with open(error_file, "w", encoding="utf-8") as f:
                f.write(f"Scrape failed on {self.today_iso}:\n")
                f.write(f"Exception Type: {err_type}\n")
                f.write(f"Message: {err_msg}\n\n")
                f.write(full_trace)
            print(f"Error log written to: {error_file}")

        finally:
            try:
                driver.quit()
            except:
                pass
            
if __name__ == "__main__":
    tatapower = Tataddl()
    tatapower.scrape()

