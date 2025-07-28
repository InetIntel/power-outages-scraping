import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TataScraper:
    def __init__(self):
        self.url = "https://customerportal.tatapower.com/TPCD/OuterOutage.aspx#"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.year = datetime.today().strftime("%Y")
        self.month = datetime.today().strftime("%m")
        self.folder = f"/data/india/tata/raw/{self.year}/{self.month}"
        os.makedirs(self.folder, exist_ok=True)

    def fetch_and_save(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        driver.get(self.url)

        wait = WebDriverWait(driver, 20)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        wait.until(EC.invisibility_of_element_located((By.ID, "page_loader")))

        btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@tabindex='1' and @aria-label='Click to List']")))
        driver.execute_script("arguments[0].scrollIntoView(true);", btn)
        btn.click()

        wait.until(EC.invisibility_of_element_located((By.ID, "page_loader")))
        wait.until(EC.presence_of_element_located((By.ID, "table1")))

        html = driver.page_source
        file_path = os.path.join(self.folder, f"power_outages.IND.tata.raw.{self.today}.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Saved: {file_path}")
        driver.quit()

if __name__ == "__main__":
    TataScraper().fetch_and_save()
