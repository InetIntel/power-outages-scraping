from bs4 import BeautifulSoup
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import traceback

BUTTON_XPATH = "//button[@type='submit' and text()='English']"
DROPDOWN_NAME = "example1_length"
TABLE_NAME = "example1"

class Nesco:

    def __init__(self):
        self.page_url = "https://nesco.portal.gov.bd/site/view/miscellaneous_info/%E0%A6%AC%E0%A6%BF%E0%A6%A6%E0%A7%8D%E0%A6%AF%E0%A7%81%E0%A7%8E-%E0%A6%AC%E0%A6%A8%E0%A7%8D%E0%A6%A7%E0%A7%87%E0%A6%B0-%E0%A6%AC%E0%A6%BF%E0%A6%9C%E0%A7%8D%E0%A6%9E%E0%A6%AA%E0%A7%8D%E0%A6%A4%E0%A6%BF"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None
        self.year = str(datetime.now().year)
        self.month = str(datetime.now().month).zfill(2)

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.images": 2,  # Block images
            "profile.managed_default_content_settings.stylesheets": 2,  # Block CSS
        })
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(self.page_url)
        self.filename = f"power_outages.BD.nesco.raw.{self.today}.html"

        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.folder_path = os.path.join(self.script_dir, 'raw', self.year, self.month)


    def check_folder(self):
        os.makedirs(self.folder_path, exist_ok=True)


    def translate(self):
        try:
            # print("Checking if element is in iframe...")
            # print("iframe count:", len(self.driver.find_elements(By.TAG_NAME, "iframe")))

            # Locate without clickability
            print("Searching for English button...")
            button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, BUTTON_XPATH))
            )
            print("Button found, attempting JS click...")
            self.driver.execute_script("arguments[0].click();", button)

            # Wait for page to finish loading
            WebDriverWait(self.driver, 20).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            print("Button clicked")

        except Exception as e:
            print("Error occurred!")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print("\nFull traceback:")
            traceback.print_exc()

    def set_rows(self, option_index=4):
        """5 options: 0=20, 1=40, 2=60, 3=80, 4=100"""
        try:
            print("Searching for dropdown...")
            dropdown = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.NAME, DROPDOWN_NAME))
            )
            print("Dropdown tag:", dropdown.tag_name)

            if dropdown.tag_name != "select":
                raise Exception("Dropdown is not a <select> tag!")

            select = Select(dropdown)
            max_rows = select.options[-1].text
            if option_index < 0 or option_index >= len(select.options):
                select.select_by_index(len(select.options) - 1)  # Select max rows
            else:
                select.select_by_index(option_index)
                max_rows = select.options[option_index].text

            # Wait for table to refresh
            WebDriverWait(self.driver, 20).until(
                EC.text_to_be_present_in_element(
                    (By.ID, TABLE_NAME + "_info"), f"Showing 1 to {max_rows}"
                )
            )
            print(f"Set rows to {max_rows} successfully.")

        except Exception as e:
            print("Error occurred!")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print("\nFull traceback:")
            traceback.print_exc()


    def fetch_and_save_html(self):
        # Wait for table to load
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

        html_content = self.driver.page_source

        with open(os.path.join(self.folder_path, self.filename), "w", encoding="utf-8") as file:
            file.write(html_content)

        print(f"HTML content saved to {os.path.join(self.folder_path, self.filename)}")


    def parse_and_save_json(self, table_id=None, table_index=0):
        with open(os.path.join(self.folder_path, self.filename), "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file.read(), "html.parser")

            # Locate table
            if table_id:
                table = soup.find("table", id=table_id)
            else:
                tables = soup.find_all("table")
                if not tables:
                    return None
                table = tables[table_index]

            if not table:
                return None

            # ---- Extract headers ----
            headers = []
            header_row = None

            thead = table.find("thead")
            if thead:
                header_row = thead.find("tr")
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]

            # If no thead or empty, use first row
            if not headers:
                first_row = table.find("tr")
                if first_row:
                    header_row = first_row
                    headers = [col.get_text(strip=True) for col in first_row.find_all(["th", "td"])]

            # ---- Extract rows ----
            data = []
            tbody = table.find("tbody")

            # If table has no <tbody>, iterate all TRs but skip headers
            rows = tbody.find_all("tr") if tbody else table.find_all("tr")

            for row in rows:
                # Skip header row
                if row is header_row:
                    continue

                cells = row.find_all(["td", "th"])
                if not cells:
                    continue

                row_data = {}
                for i, cell in enumerate(cells):
                    h = headers[i] if i < len(headers) else f"column_{i}"
                    row_data[h] = cell.get_text(strip=True)

                if any(row_data.values()):
                    data.append(row_data)

            # ---- Save JSON ----
            output_filename = f"power_outages.BD.nesco.raw.{self.today}.json"

            with open(os.path.join(self.folder_path, output_filename), "w", encoding="utf-8") as outfile:
                json.dump(data, outfile, indent=2, ensure_ascii=False)

            print(f"Parsed data saved to {os.path.join(self.folder_path, output_filename)}")


    def scrape(self):
        self.check_folder()
        # self.translate()
        self.set_rows()
        self.fetch_and_save_html()
        self.parse_and_save_json()
        self.driver.quit()


if __name__ == "__main__":
    nesco = Nesco()
    nesco.scrape()