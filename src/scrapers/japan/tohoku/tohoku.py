import json
import ssl
import requests
from urllib.request import urlopen, Request
from datetime import datetime
from pathlib import Path


class TohokuScraper:
    """Scraper for Tohoku Electric Power Co. JSON outage data (relaxed SSL by default)."""

    def __init__(self):
        self.provider = "tohoku"
        self.country = "japan"
        self.country_code = "JP"
        self.feed_base = "https://nw.tohoku-epco.co.jp/teideninfo/blackout/"
        self.base_path = Path(__file__).resolve().parent / "data" / "raw"
        # self.base_path = Path("/dagu/data") 
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.today_iso = datetime.now().strftime("%Y-%m-%d")

        # Preconfigure SSL context (reduced security level to allow older servers)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.set_ciphers("DEFAULT:@SECLEVEL=1")

        # Common headers
        self.headers = {"User-Agent": "Mozilla/5.0 (compatible; outage-scraper/1.0)"}

    def fetch_json(self, index: int):
        """Fetch rirekiinfoXX.json (01–07) using a downgraded SSL context."""
        file_name = f"rirekiinfo{index:02}.json"
        url = self.feed_base + file_name
        print(f"[TOHOKU] Fetching: {url}")

        try:
            req = Request(url, headers=self.headers)
            with urlopen(req, context=self.ssl_context) as r:
                data = r.read().decode("utf-8")
                return json.loads(data)
        except Exception as e:
            print(f"Failed to fetch {file_name}: {e}")
            return None

    def run(self):
        """Fetch rirekiinfo01–07.json and save combined weekly JSON."""
        all_data = []
        for i in range(1, 8):
            data = self.fetch_json(i)
            if data:
                all_data.append(data)

        if not all_data:
            print("No data collected.")
            return

        combined = {
            "provider": self.provider,
            "country": self.country,
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "entries": all_data,
        }

        output_path = (
            self.base_path
            / f"power_outages.{self.country_code}.{self.provider}.raw.{self.today_iso}.json"
        )

        output_path.write_text(
            json.dumps(combined, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        print(f"Saved combined weekly JSON → {output_path}")



if __name__ == "__main__":
    TohokuScraper().run()
