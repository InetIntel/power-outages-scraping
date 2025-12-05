import os
import requests
from datetime import datetime, timedelta, timezone

class ChugokuScraper:
    """Scraper for Chugoku Electric Power (中国電力) outage page (raw HTML)."""

    def __init__(self):
        self.provider = "chugoku"
        self.country = "japan"
        self.country_code = "JP"

        # Base URL and time zone
        self.url = "https://www.teideninfo.energia.co.jp/LWC30040/index"
        self.JST = timezone(timedelta(hours=9))  # Japan Standard Time

        # Directory setup (save locally under ./data)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, "data")
        os.makedirs(self.data_dir, exist_ok=True)

    def fetch_raw_html(self):
        """Download raw outage page and save it locally."""
        date_param = datetime.now(self.JST).strftime("%Y%m%d")
        params = {"date": date_param, "type": ""}

        print(f"[SCRAPER] Fetching Chugoku outage info for Japan date: {date_param}")
        response = requests.get(self.url, params=params, timeout=15)
        response.raise_for_status()

        timestamp = datetime.now(self.JST).strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"power_outages.{self.country_code}.{self.provider}.raw.{timestamp}.html"
        file_path = os.path.join(self.data_dir, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(response.text)

        print(f"[SCRAPER] Saved raw HTML → {file_path}")
        return file_path

    def run(self):
        """Run the scraper."""
        saved_path = self.fetch_raw_html()
        print(f"[DONE] HTML successfully saved: {saved_path}")


if __name__ == "__main__":
    scraper = ChugokuScraper()
    scraper.run()
