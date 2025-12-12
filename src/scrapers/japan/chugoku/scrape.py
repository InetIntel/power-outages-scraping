import os
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path


class ChugokuHistoryScraper:
    """Scraper for Chugoku Electric Power — save raw HTML only."""

    BASE_URL = "https://www.teideninfo.energia.co.jp/LWC30040/index"

    def __init__(self):
        # Save to: <this_dir>/data/raw/
        self.base_path = Path(__file__).resolve().parent / "data" / "raw"
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.JST = timezone(timedelta(hours=9))

    def fetch_html(self, date_str):
        params = {"date": date_str, "type": ""}

        resp = requests.get(self.BASE_URL, params=params, timeout=15)
        resp.raise_for_status()

        return resp.text

  
    def save_html(self, date_str, html):
        filepath = self.base_path / f"{date_str}.html"
        filepath.write_text(html, encoding="utf-8")

        print(f"[SAVED HTML] {filepath}")
        return filepath


    def run_single_day(self, date_str):
        html = self.fetch_html(date_str)
        return self.save_html(date_str, html)


    def run_last_n_days(self, n=8):
        today = datetime.now(self.JST)

        for i in range(n):
            d = today - timedelta(days=i)
            date_str = d.strftime("%Y%m%d")

            try:
                self.run_single_day(date_str)
            except Exception as e:
                print(f"[ERROR] Failed for {date_str}: {e}")



if __name__ == "__main__":
    scraper = ChugokuHistoryScraper()
    scraper.run_last_n_days(8)
