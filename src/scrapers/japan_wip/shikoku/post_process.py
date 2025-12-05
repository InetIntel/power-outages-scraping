import os
import json
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
from pathlib import Path


class ShikokuProcessor:
    """
    Processor for Shikoku Electric Power Network (四国電力送配電株式会社).
    Reads all raw HTML files under ./data and extracts outage information.
    """

    def __init__(self):
        self.provider = "shikoku"
        self.country = "japan"
        self.country_code = "JP"

        # Japan Standard Time (UTC+9)
        self.JST = timezone(timedelta(hours=9))
        self.today = datetime.now(self.JST)
        self.today_iso = self.today.strftime("%Y-%m-%d")

        # Data folder (same directory as this script)
        self.base_dir = Path(__file__).resolve().parent
        self.data_dir = self.base_dir / "data"
        self.data_dir.mkdir(exist_ok=True)

    def _parse_html(self, html_text: str) -> list:
        """
        Extract outage entries from the HTML.
        This works even if table structure changes slightly.
        """
        soup = BeautifulSoup(html_text, "html.parser")
        outages = []

        # Common structure: tables or div lists
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            headers = [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])] if rows else []

            for row in rows[1:]:
                cols = [td.get_text(strip=True) for td in row.find_all("td")]
                if not cols:
                    continue

                outage = dict(zip(headers, cols))
                outages.append(outage)

        # If no tables found, fallback: search div/list structure
        if not outages:
            for div in soup.find_all("div", class_="outage-info"):
                text = div.get_text(" ", strip=True)
                if text:
                    outages.append({"raw_text": text})

        return outages

    def run(self):
        """
        Parse all raw HTML files and combine into a single processed JSON file.
        """
        all_outages = []

        for file in sorted(self.data_dir.glob("*.html")):
            print(f"[PROCESS] Parsing {file.name}")
            html = file.read_text(encoding="utf-8", errors="ignore")
            entries = self._parse_html(html)
            if entries:
                all_outages.extend(entries)

        if not all_outages:
            print("No outages found in any HTML file.")
            return

        # Output file
        output_file = (
            self.data_dir
            / f"power_outages.{self.country_code}.{self.provider}.processed.{self.today_iso}.json"
        )

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_outages, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Parsed {len(all_outages)} outages → {output_file.name}")
        return output_file


if __name__ == "__main__":
    processor = ShikokuProcessor()
    processor.run()
