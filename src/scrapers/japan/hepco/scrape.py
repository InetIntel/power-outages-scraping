# scraper_hepco.py
import requests
from datetime import datetime
from pathlib import Path


class HEPCO:
    """
    Scraper for Hokkaido Electric Power Co. (HEPCO) outage history page.
    Saves the HTML using this pattern:
        power_outages.JP.hepco.raw.YYYY-MM-DD.html
    """

    def __init__(self):
        self.provider = "hepco"
        self.country = "japan"
        self.country_code = "JP"
        self.base_path = Path(__file__).resolve().parent / "data" / "raw"
       
        target_date = datetime.now()

        # Common formatted date strings
        self.today_iso = target_date.strftime("%Y-%m-%d")  
        self.today_jp = target_date.strftime("%m-%d-%Y")   
        self.year = target_date.strftime("%Y")
        self.month = target_date.strftime("%m")

        # Target URL
        self.url = "https://teiden-info.hepco.co.jp/past00000000.html"

        # HTTP headers
        self.headers = {"User-Agent": "Mozilla/5.0 (compatible; outage-scraper/1.0)"}

    def _get_output_path(self):
        """Generate the daily output path and filename."""
        filename = f"power_outages.{self.country_code}.{self.provider}.raw.{self.today_iso}.html"
        return self.base_path / filename

    def fetch_html(self):
        """Fetch the HEPCO outage page."""
        print(f"[{self.provider.upper()}] Fetching: {self.url}")
        response = requests.get(self.url, headers=self.headers, timeout=15)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response.text

    def save_html(self, html):
        """Save fetched HTML to a local file."""
        output_path = self._get_output_path()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")
        print(f"[{self.provider.upper()}] Saved HTML → {output_path.relative_to(Path.cwd())}")
        return output_path

    def run(self):
        """Main execution function."""
        html = self.fetch_html()
        return self.save_html(html)


if __name__ == "__main__":
    scraper = HEPCO()
    scraper.run()
