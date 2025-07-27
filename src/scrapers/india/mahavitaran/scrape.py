import os
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

class MahavitaranScraper:
    def __init__(self):
        self.provider = "mahavitaran"
        self.country = "india"
        self.base_path = "/data"
        self.url = "https://www.mahadiscom.in/consumer/en/weekly-outage-data/"

        month_label = self.get_month_label()
        month_abbr = month_label.split("-")[0]
        self.year = str(datetime.now().year)
        self.month = datetime.strptime(month_abbr, "%b").strftime("%m")
        self.target_month = month_label
        self.page = 1

    def create_folder(self, data_type, day):
        folder = os.path.join(
            self.base_path,
            self.country,
            self.provider,
            data_type,
            self.year,
            self.month,
            day
        )
        os.makedirs(folder, exist_ok=True)
        return folder

    def get_month_label(self):
        res = requests.get(self.url)
        soup = BeautifulSoup(res.content, 'html.parser')
        select = soup.find('select', class_='shd_select')
        return select.find_all('option')[0].get_text(strip=True)

    def get_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.binary_location = "/usr/bin/chromium-browser"
        service = webdriver.chrome.service.Service("/usr/bin/chromedriver")
        return webdriver.Chrome(service=service, options=options)

    def scrape(self):
        driver = self.get_driver()
        try:
            driver.get(self.url)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "shd_select")))
            Select(driver.find_element(By.ID, "shd_select")).select_by_visible_text(self.target_month)

            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "wo_shd_table_length")))
            Select(driver.find_element(By.NAME, "wo_shd_table_length")).select_by_value("10")
            time.sleep(2)

            while True:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "wo_shd_table")))
                html = driver.page_source

                # Parse to extract the date from the first row of the table
                soup = BeautifulSoup(html, 'html.parser')
                first_row = soup.select_one("#wo_shd_table tbody tr td")
                if first_row:
                    try:
                        row_date = datetime.strptime(first_row.text.strip(), "%d-%m-%Y").strftime("%d")
                    except Exception:
                        row_date = datetime.now().strftime("%d")
                else:
                    row_date = datetime.now().strftime("%d")

                folder = self.create_folder("raw", row_date)
                filename = f"power_outages.IND.{self.provider}.raw.{self.year}-{self.month}-{row_date}_{self.page}.html"
                path = os.path.join(folder, filename)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"Saved page {self.page} to {path}")
                self.page += 1

                next_btn = driver.find_element(By.CSS_SELECTOR, ".paginate_button.next")
                if next_btn.get_attribute("tabindex") == "-1":
                    break
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(2)

        finally:
            driver.quit()
            print("Scraping complete.")

if __name__ == "__main__":
    MahavitaranScraper().scrape()
