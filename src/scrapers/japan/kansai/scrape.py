import json
import ssl
import requests
from urllib.request import urlopen, Request
from datetime import datetime, timedelta, timezone
from pathlib import Path


class KansaiScraper:
    """Scraper for Kansai Transmission and Distribution JSON outage history (relaxed SSL)."""

    def __init__(self):
        self.provider = "kansai"
        self.country = "japan"
        self.country_code = "JP"
        self.feed_url = "https://www.kansai-td.co.jp/interchange/teiden-info/ja/history.json"

        self.base_path = Path(__file__).resolve().parent / "data" / "raw"
        # self.base_path = Path("/dagu/data")
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Japan local date (for filename)
        JST = timezone(timedelta(hours=9))
        self.today_iso = datetime.now(JST).strftime("%Y-%m-%d")
        self.jst_now = datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")

        # Preconfigure SSL context
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.set_ciphers("DEFAULT:@SECLEVEL=1")

        # Common headers
        self.headers = {"User-Agent": "Mozilla/5.0 (compatible; outage-scraper/1.0)"}

    def fetch_json(self):
        """Fetch JSON data from the Kansai endpoint with timestamp parameter."""
        JST = timezone(timedelta(hours=9))
        timestamp = datetime.now(JST).strftime("%Y%m%d%H%M")
        url = f"{self.feed_url}?_={timestamp}"
        print(f"[KANSAI] Fetching: {url}")

        try:
            req = Request(url, headers=self.headers)
            with urlopen(req, context=self.ssl_context) as r:
                data = r.read().decode("utf-8")
                return json.loads(data)
        except Exception as e:
            print(f"Failed to fetch Kansai data: {e}")
            return None

    def run(self):
        data = self.fetch_json()
        if not data:
            print("No data collected.")
            return

        combined = {
            "provider": self.provider,
            "country": self.country,
            "fetched_at": self.jst_now,
            "entries": data,
        }

        output_path = (
            self.base_path
            / f"power_outages.{self.country_code}.{self.provider}.raw.{self.today_iso}.json"
        )

        output_path.write_text(
            json.dumps(combined, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        print(f"Saved Kansai outage JSON → {output_path}")


if __name__ == "__main__":
    KansaiScraper().run()
