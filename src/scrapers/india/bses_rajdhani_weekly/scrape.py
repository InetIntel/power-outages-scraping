import os
import time
import traceback
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class BSESRajdhani:
    def __init__(self):
        self.provider = "bses_rajdhani_weekly"
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
        self.url = "https://www.bsesdelhi.com/web/brpl/maintenance-outage-schedule"

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
        return webdriver.Chrome(service=service, options=options)

    def scrape(self):
        raw_folder = self.create_folder("raw")
        driver = self.get_chrome_driver()
        try:
            driver.get(self.url)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "select")))
            dropdowns = driver.find_elements(By.TAG_NAME, "select")

            print(f"Using date for selection: {self.today_indian}")
            try:
                Select(dropdowns[0]).select_by_value(self.today_indian)
            except Exception as e:
                print(f"Date not available in dropdown: {self.today_indian}")
                with open(os.path.join(raw_folder, f"404_{self.today_iso}.txt"), "w", encoding="utf-8") as f:
                    f.write(f"No dropdown entry for {self.today_indian}: {type(e).__name__} - {str(e)}\n")
                driver.quit()
                return

            time.sleep(1)

            WebDriverWait(driver, 10).until(
                lambda d: len(Select(driver.find_elements(By.TAG_NAME, "select")[1]).options) > 1
            )

            dropdowns = driver.find_elements(By.TAG_NAME, "select")
            division_select = Select(dropdowns[1])
            div_options = [opt.text.strip() for opt in division_select.options]

            selected_division = None
            for opt in div_options:
                if opt.lower() == "all division":
                    selected_division = opt
                    break
            for opt in div_options:
                if opt.lower() != "select division":
                    selected_division = selected_division or opt
                    break

            if not selected_division:
                raise Exception("No valid division options found.")

            division_select.select_by_visible_text(selected_division)
            print(f"Division dropdown options: {div_options}")
            print(f"Selected division: {selected_division}")

            search_btn = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Search')]"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_btn)
            time.sleep(0.5)

            try:
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Search')]")))
                search_btn.click()
            except Exception:
                print("Standard click failed, using JS click...")
                driver.execute_script("arguments[0].click();", search_btn)

            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//tbody[@id='maintainanceScheduleData']/tr"))
            )

            html = driver.page_source

            file_path = os.path.join(raw_folder, f"power_outages.IND.{self.provider}.raw.{self.today_iso}.html")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Saved entire page HTML: {file_path}")

        except Exception as e:
            print(f"Scraping failed: {type(e).__name__}: {e}")
            traceback.print_exc()
            with open(os.path.join(raw_folder, f"404_{self.today_iso}.txt"), "w", encoding="utf-8") as f:
                f.write(f"Scrape failed for {self.today_indian}: {type(e).__name__}: {str(e)}\n")
        finally:
            driver.quit()

if __name__ == "__main__":
    BSESRajdhani().scrape()
