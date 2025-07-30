import os
import time
import traceback
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class Mahavitaran:
    def __init__(self):
        self.provider = "mahavitaran"
        self.country = "india"
        self.base_path = "/data"
        
        # Optional debug date (format: DD-MM-YYYY)
        # target_date = datetime.strptime("05-06-2025", "%d-%m-%Y")  # DEBUG
        
        # today if debug not set
        target_date = datetime.now()
        
        self.today_iso = target_date.strftime("%Y-%m-%d")
        self.today_indian = target_date.strftime("%d-%m-%Y")  # DD-MM-YYYY
        self.year = target_date.strftime("%Y")
        self.month = target_date.strftime("%m")
        self.url = "https://www.mahadiscom.in/consumer/en/weekly-outage-data/"

    def create_folder(self, data_type):
        folder_path = os.path.join(self.base_path, self.country, self.provider, data_type, self.year, self.month)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def get_month_label(self):
        try:
            res = requests.get(self.url, timeout=10)
            soup = BeautifulSoup(res.content, 'html.parser')
            select = soup.find('select', class_='shd_select')
            if select and select.find_all('option'):
                return select.find_all('option')[0].get_text(strip=True)
            else:
                raise Exception("No month options found in dropdown")
        except Exception as e:
            raise Exception(f"Failed to get month label: {str(e)}")

    def get_chrome_driver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.binary_location = "/usr/bin/chromium-browser"
        service = Service("/usr/bin/chromedriver")
        return webdriver.Chrome(service=service, options=options)

    def scrape(self):
        raw_folder = self.create_folder("raw")
        driver = self.get_chrome_driver()
        
        try:
            # Get the current month label
            target_month = self.get_month_label()
            print(f"Scraping data for month: {target_month}")
            
            driver.get(self.url)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "shd_select")))
            
            # Select the current month
            Select(driver.find_element(By.ID, "shd_select")).select_by_visible_text(target_month)
            
            # Set table to show all entries (avoid pagination)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "wo_shd_table_length")))
            select_length = Select(driver.find_element(By.NAME, "wo_shd_table_length"))
            # Try to select "All" or the highest number available
            options = [option.get_attribute("value") for option in select_length.options]
            if "-1" in options:  # "All" option
                select_length.select_by_value("-1")
            else:
                # Select the highest number available
                max_option = max([int(opt) for opt in options if opt.isdigit()])
                select_length.select_by_value(str(max_option))
            
            time.sleep(3)  # Wait for table to load
            
            # Wait for table to be present and get the full page
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "wo_shd_table")))
            
            # Check if table has data
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            table_rows = soup.select("#wo_shd_table tbody tr")
            
            if not table_rows or len(table_rows) == 0:
                print("No data rows found in table")
                with open(os.path.join(raw_folder, f"404_{self.today_iso}.txt"), "w", encoding="utf-8") as f:
                    f.write(f"No weekly outage data found for {self.today_iso}\n")
                return
            
            # Save the complete page with all data
            html = driver.page_source
            file_path = os.path.join(raw_folder, f"power_outages.IND.{self.provider}.raw.{self.today_iso}.html")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Saved raw weekly outage data: {file_path}")
            print(f"Found {len(table_rows)} data rows")

        except Exception as e:
            print(f"Scraping failed: {type(e).__name__}: {e}")
            traceback.print_exc()
            with open(os.path.join(raw_folder, f"404_{self.today_iso}.txt"), "w", encoding="utf-8") as f:
                f.write(f"Scrape failed for {self.today_indian}: {type(e).__name__}: {str(e)}\n")
        finally:
            driver.quit()

if __name__ == "__main__":
    Mahavitaran().scrape()