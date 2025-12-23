import time
import os
from pathlib import Path
from utils import Uploader
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

class IberdrolaSpider:
    def __init__(self):

        # create uploader to upload data to minio
        self.uploader = Uploader("spain")

        # Set path to download planned outage pdfs locally to docker container before uploading to minio
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.download_dir = os.path.join(self.script_dir, 'planned_outage_pdfs')
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir, exist_ok=True)

        # Set options for Chrome Webdriver
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--remote-debugging-port=0")

        # Set download options for Chrome Webdriver
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_setting_values.automatic_downloads": 1,
        }
        options.add_experimental_option("prefs", prefs)

        # Hide that driver is headless so full website is accessible
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--lang=es-ES")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Create web driver using options from above
        self.driver = webdriver.Chrome(options=options)

        # Start at main power provider page that has links to different regions
        self.base_url = "https://www.i-de.es/outages-scheduled-power-cuts/scheduled-power-cuts"

    def get_region_links(self):
        """
        Navigate to Iberdrola scheduled outages page and scrape
        the list of provinces with their corresponding outage URLs.

        Returns:
            list[list[str, str]]: Each element is [region_name, region_url]
        """

        # start at main page with links to regions
        self.driver.get(self.base_url)

        # store links to different regions as they're collected
        region_links = []

        # check if region links are present on page
        try:
            # Wait until all province <td> elements are loaded on the page
            td_elements = WebDriverWait(self.driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "td.td20.card-center"))
            )

            # for each region
            for td in td_elements:
                # Extract region name from the <td>'s onclick attribute
                td_onclick = td.get_attribute("onclick")
                region_name = ""
                if td_onclick and "event_label" in td_onclick:
                    # Parse out the "event_label" string from the onclick attribute
                    start = td_onclick.find("event_label") + len("event_label")
                    start = td_onclick.find(":", start) + 1
                    end = td_onclick.find("})", start)
                    region_name = td_onclick[start:end].strip(" ':")  # clean up extra chars

                # Extract the planned outages URL from the nested <div>'s onclick attribute
                try:
                    div = td.find_element(By.CSS_SELECTOR, "div.contenedor-medium.custom-card")
                    onclick_attr = div.get_attribute("onclick")
                    if onclick_attr and "abrirUrl" in onclick_attr:
                        # Parse the relative URL out of abrirUrl('/path')
                        start = onclick_attr.find("('") + 2
                        end = onclick_attr.find("')", start)
                        relative_url = onclick_attr[start:end].split(",")[0].strip().strip("'")
                        full_url = "https://www.i-de.es" + relative_url
                        region_links.append([region_name, full_url])
                except:
                    # If something goes wrong for one region, skip it and continue
                    continue

        except Exception as e:
            # if page structure has updated and links cannot be found
            print("Could not find region links:", e)

        return region_links

    def get_region_pdfs(self, region_links):
        """
        For each [region_name, region_url], open the page, find the
        single 'Descargar'(download) link to a PDF.

        Returns:
            list[]: List of pdf download links.
        """

        # store pdf url's as they're collected
        pdf_urls = []

        # iterate through each region
        for region_name, region_url in region_links:

            # reset connection between sites, else can only reach to first site
            self.driver.get("about:blank")
            self.driver.delete_all_cookies()
            # Clear cache to force a clean fetch (Chrome DevTools Protocol)
            try:
                self.driver.execute_cdp_cmd("Network.clearBrowserCache", {})
                self.driver.execute_cdp_cmd("Network.clearBrowserCookies", {})
            except Exception:
                pass

            # go to current region page
            self.driver.get(region_url)

            # Wait for the download button to be available
            try:
                link = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR,
                        "a[href*='/documents/d/guest/']"
                    ))
                )
            except Exception:
                print(f"[INFO] No 'Descargar' PDF link found for {region_name}: {region_url}")
                continue

            # get link to pdf if available
            pdf_url = (link.get_attribute("href") or "").strip()
            if pdf_url:
                pdf_urls.append(pdf_url)

        # return list of pdf links
        return pdf_urls

    def download_pdfs(self, pdf_urls, timeout=30):
        """
        Iterate through pdf links and download them to local container storage.
        """

        # make sure download directory exists, else create it
        os.makedirs(self.download_dir, exist_ok=True)
        dl_dir = Path(self.download_dir)

        # iterate through pdf links
        for url in pdf_urls:

            # snapshot of current files in download directory
            before = set(os.listdir(dl_dir))

            # trigger download
            self.driver.get(url)

            # wait for a new file to finish downloading
            end = time.time() + timeout
            new_file = None
            while time.time() < end:
                time.sleep(0.1)
                current = set(os.listdir(dl_dir))
                diff = list(current - before)
                if diff:
                    new_file = dl_dir / diff[0]
                    # skip partial downloads
                    if new_file.suffix == ".crdownload":
                        continue
                    break

            if not new_file or not new_file.exists():
                print(f"  [!] Timeout: {url}")
                continue

            # ensure .pdf extension
            if new_file.suffix.lower() != ".pdf":
                new_name = new_file.with_suffix(".pdf")
                new_file.rename(new_name)
                new_file = new_name
            # add date to filename
            now = datetime.now()
            current_year = f"{now.year}"
            current_month = f"{now.month:02d}"
            current_day = f"{now.day:02d}"
            name, ext = os.path.splitext(new_file.name)
            dated_file = f"{name}_{current_day}_{current_month}_{current_year}{ext}"
            new_file.rename(new_file.with_name(dated_file))

    def upload(self):
        """
        Upload PDFs to minio storage.
        """
        now = datetime.now()
        current_year = f"{now.year}"
        current_month = f"{now.month:02d}"
        base = os.path.abspath(self.download_dir)
        for root, _, files in os.walk(base):
            for file in files:
                if file.startswith("SGS "): #skip "SGS..." file, not sure why this gets downloaded sometimes
                    continue
                # append date to filename
                local_path = os.path.join(root, file)
                rel_path = os.path.relpath(local_path, base).replace("\\", "/")
                s3_path = f"iberdrola_planned/raw/{current_year}/{current_month}/{rel_path}"
                self.uploader.upload_file(local_path, s3_path)

    def close(self):
        """
        Closes the browser session cleanly.
        """
        self.driver.quit()

if __name__ == "__main__":

    # Initialize spider
    spider = IberdrolaSpider()

    # Get all region links
    links = spider.get_region_links()

    # Get PDF links for each region
    pdf_urls = spider.get_region_pdfs(links[:5])

    # save pdfs locally to docker container
    spider.download_pdfs(pdf_urls)

    # close the browser
    spider.close()

    # upload raw data to minio
    spider.upload()