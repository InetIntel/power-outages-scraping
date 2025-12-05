import os
import requests
from datetime import datetime, timezone, timedelta

class ShikokuScraper:
    """Scraper for Shikoku Electric Power Network (四国電力送配電株式会社) outage history pages."""

    def __init__(self, index=None):
        self.provider = "shikoku"
        self.country = "japan"
        self.base_url = "https://www.yonden.co.jp/nw/teiden-info/"
        self.index = index  # None for base history.html, or int 1–7 for numbered pages

        # Japan Standard Time (UTC+9)
        self.JST = timezone(timedelta(hours=9))

        # Local /data directory (same style as Chugoku)
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)

    def get_url(self):
        """Return the correct page URL."""
        if self.index is None:
            return self.base_url + "history.html"
        else:
            return self.base_url + f"history{self.index:02d}.html"

    def scrape(self):
        """Download and save the raw HTML to the local data/ folder."""
        url = self.get_url()
        print(f"[SHIKOKU] Fetching: {url}")

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
        except Exception as e:
            print(f"[SHIKOKU] Failed to fetch {url}: {e}")
            return None

        # File name includes page index and timestamp
        timestamp = datetime.now(self.JST).strftime("%Y%m%d_%H%M%S")
        index_str = self.index if self.index is not None else "00"
        filename = f"{self.provider}_history_{index_str}_{timestamp}.html"
        filepath = os.path.join(self.data_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(response.text)

        print(f"[SHIKOKU] Saved raw HTML → {filepath}")
        return filepath


if __name__ == "__main__":
    # Scrape base page and history01–07
    scraper = ShikokuScraper()
    scraper.scrape()

    for i in range(1, 8):
        scraper = ShikokuScraper(index=i)
        scraper.scrape()
