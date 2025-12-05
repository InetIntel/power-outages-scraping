import requests
from datetime import datetime, timedelta
from pathlib import Path


class TEPCOScraper:


    def __init__(self):
        self.provider = "tepco"
        self.country = "japan"
        self.country_code = "JP"
        self.base_path = Path(__file__).resolve().parent / "data"

        # TEPCO XML base URL
        self.base_url = "https://teideninfo.tepco.co.jp/day/teiden/"

        # Create directory
        self.base_path.mkdir(parents=True, exist_ok=True)
        (self.base_path / "raw").mkdir(parents=True, exist_ok=True)


        # HTTP headers
        self.headers = {"User-Agent": "Mozilla/5.0 (compatible; outage-scraper/1.0)"}

        # Date fields
        self.today = datetime.now()
        self.today_iso = self.today.strftime("%Y-%m-%d")
        self.year = self.today.strftime("%Y")
        self.month = self.today.strftime("%m")

    def _get_output_path(self, date: datetime):
        """Return file path for a given date (power_outages.JP.tepco.raw.YYYY-MM-DD.xml)."""
        date_str = date.strftime("%Y-%m-%d")
        filename = f"power_outages.{self.country_code}.{self.provider}.raw.{date_str}.xml"
        return self.base_path / "raw" / filename

    def _get_remote_filename(self, date: datetime):
        """Return the remote file name pattern TEPCO uses (e.g., day001-j.xml)."""
        delta_days = (self.today - date).days
        if delta_days == 0:
            return "index-j.xml"
        else:
            return f"day{delta_days:03}-j.xml"

    def fetch_and_save(self, date: datetime):
        """Fetch a single day’s XML and save to local storage."""
        remote_filename = self._get_remote_filename(date)
        url = self.base_url + remote_filename

        print(f"[{self.provider.upper()}] Fetching: {url}")
        response = requests.get(url, headers=self.headers, timeout=15)
        response.raise_for_status()

        output_path = self._get_output_path(date)
        output_path.write_bytes(response.content)

        print(f"[{self.provider.upper()}] Saved XML → {output_path.relative_to(Path.cwd())}")
        return output_path

    def run(self, days_back: int = 7):
        """
        Fetch outage XML data for the past `days_back` days.
        Default: last 7 days + today (8 total).
        """
        for i in range(days_back + 1):
            date = self.today - timedelta(days=i)
            try:
                self.fetch_and_save(date)
            except Exception as e:
                print(f"Skipped {date.strftime('%Y-%m-%d')} due to: {e}")


if __name__ == "__main__":
    scraper = TEPCOScraper()
    scraper.run()
