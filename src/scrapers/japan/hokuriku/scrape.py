import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path

JST = timezone(timedelta(hours=9))  # Japan Standard Time

class RikudenHTMLScraper:
    def __init__(self):
        # Get today's date in JST
        self.today_jst = datetime.now(JST)
        self.date_str = self.today_jst.strftime("%Y%m%d")

        # Build URL using JST date
        self.url = f"https://www.rikuden.co.jp/nw/teiden/f2/sevendays/{self.date_str}/otj600.html"

        # Save raw HTML under provider folder
        self.data_dir = Path(__file__).resolve().parent / "data" / "raw"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def fetch_html(self):
        resp = requests.get(self.url, timeout=20)
        resp.raise_for_status()
        return resp.content  

    def save_html(self, content):
        timestamp = self.today_jst.strftime("%Y%m%dT%H%M%S")
        filename = f"rikuden_{self.date_str}_{timestamp}.html"
        path = self.data_dir / filename

        path.write_bytes(content)
        print(f"Saved HTML → {path}")

    def run(self):
        html_bytes = self.fetch_html()
        self.save_html(html_bytes)

if __name__ == "__main__":
    scraper = RikudenHTMLScraper()
    scraper.run()
