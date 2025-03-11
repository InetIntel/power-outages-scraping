import os
import time
import requests
from datetime import datetime
import pytesseract
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Tnpdcl:
    def __init__(self):
        self.url = 'https://www.tnebltd.gov.in/outages/viewshutdown.xhtml'
        self.base_url = "https://www.tnebltd.gov.in/outages/"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None


    def check_folder(self):
        self.folder_path = os.path.abspath("./data/" + self.today)
        os.makedirs(self.folder_path, exist_ok=True)
        options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": self.folder_path,
            "download.prompt_for_download": False,
            "directory_upgrade": True
        }
        options.add_experimental_option("prefs", prefs)
        return options

    def fetch(self):
        options = self.check_folder()
        options.add_experimental_option("detach", False)
        driver = webdriver.Chrome(options=options)
        driver.get(self.url)
        wait = WebDriverWait(driver, 20)
        wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        return driver

    def get_file(self, driver, number):
        wait = WebDriverWait(driver, 20)
        input_element = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//*[substring(@id, string-length(@id) - string-length(':cap') + 1) = ':cap']")
        ))
        input_element.clear()
        input_element.send_keys(number)
        submit_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//*[substring(@id, string-length(@id) - string-length(':submit3') + 1) = ':submit3']")
        ))
        submit_button.click()
        excel_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn.btn-default.buttons-excel.buttons-html5")))
        excel_button.click()
        time.sleep(2)
        driver.quit()



    def getNumber(self, driver):
        wait = WebDriverWait(driver, 20)
        img_element = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//*[substring(@id, string-length(@id) - string-length(':imgCaptchaId') + 1) = ':imgCaptchaId']")
        ))
        img_src = img_element.get_attribute("src")
        response = requests.get(img_src, stream=True)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            captcha_text = pytesseract.image_to_string(img, config="--psm 6")
            return captcha_text.strip()
        else:
            print("Failed to download CAPTCHA image.")


    def scrape(self):
        driver = self.fetch()
        number = self.getNumber(driver)
        self.get_file(driver, number)
        print("scraping is done for tnebltd")





# tnebltd = Tnpdcl()
# tnebltd.scrape()


