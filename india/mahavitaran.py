import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.support.wait import WebDriverWait
from datetime import datetime


class Mahavitaran:

    def __init__(self):
        self.url = "https://www.mahadiscom.in/consumer/en/weekly-outage-data/"
        self.current_month = datetime.today().strftime("%Y-%m")
        self.month = self.get_months(self.url)
        self.folder_path = None
        self.check_folder()
        self.page = 1


    def check_folder(self):
        self.folder_path = "./monthy_data/" + self.current_month
        os.makedirs(self.folder_path, exist_ok=True)


    def fetch(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=options)
        driver.get(self.url)
        time.sleep(2)
        return driver

    def selection(self, driver):
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.ID, "shd_select")))
        select_element = Select(driver.find_element(By.ID, "shd_select"))
        select_element.select_by_visible_text(self.month)

        wait.until(EC.presence_of_element_located((By.NAME, "wo_shd_table_length")))
        select_element = Select(driver.find_element(By.NAME, "wo_shd_table_length"))
        select_element.select_by_value(str(10))

        self.save_table_data(driver)

    def save_table_data(self, driver):
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.ID, "wo_shd_table")))
        table = driver.find_element(By.ID, "wo_shd_table")
        table_html = table.get_attribute('outerHTML')
        full_html = f"<html><body>{table_html}</body></html>"
        file_path = os.path.join(self.folder_path, self.month + "_" + str(self.page) + "_outage_data.html")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(full_html)
        print("Table data saved to table_data.html")
        self.page += 1




    def scrape(self):
        driver = self.fetch()
        self.selection(driver)

        while True:
            wait = WebDriverWait(driver, 20)
            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".paginate_button.next")))
            driver.execute_script("arguments[0].scrollIntoView();", next_button)
            tabindex = next_button.get_attribute("tabindex")
            if tabindex == "-1":
                break
            next_button.click()
            time.sleep(2)
            self.save_table_data(driver)

        driver.quit()
        print("scraping is done for mahadiscom")


    def get_months(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        select_element = soup.find('select', class_='shd_select')
        options = select_element.find_all('option')
        month = options[0].get_text()
        # options_text = [option.get_text() for option in options]
        return month


# mahadiscom = Mahavitaran()
# mahadiscom.scrape()
