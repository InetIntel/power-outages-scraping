import requests
from pathlib import Path
from datetime import datetime
from xml.etree import ElementTree as ET

class ShikokuScraper:
    """Scraper for Shikoku power outage XML data (四国電力)."""

    def __init__(self):
        # Consistent data/raw folder
        self.base_path = Path(__file__).resolve().parent / "data" / "raw"
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Master XML URL
        self.master_url = "https://www.okidenmail.jp/bosai/xml/history_normal.xml"

    def fetch_master_xml(self):
        ts = int(datetime.now().timestamp() * 1000)
        url = f"{self.master_url}?_={ts}"
        print(f"[OKIDEN] Fetching master XML: {url}")

        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            print(f"[ERROR] Failed to fetch master XML: {e}")
            return None

        master_text = resp.text
        master_path = self.base_path / f"okiden_master_{ts}.xml"
        master_path.write_text(master_text, encoding="utf-8")
        print(f"[OKIDEN] Saved master XML → {master_path.name}")
        return master_path, master_text

    def parse_date_keys(self, master_text):
        """Extract date keys from master XML."""
        try:
            root = ET.fromstring(master_text)
        except ET.ParseError as e:
            print(f"[ERROR] Failed to parse master XML: {e}")
            return []

        # All <data><date_key> nodes
        date_keys = [elem.text for elem in root.findall(".//data/date_key") if elem.text]
        print(f"[OKIDEN] Found {len(date_keys)} date keys")
        return date_keys

    def fetch_detail_xml(self, date_key):
        ts = int(datetime.now().timestamp() * 1000)
        url = f"https://www.okidenmail.jp/bosai/api/xml_map2.php?date_key={date_key}&_={ts}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            print(f"[ERROR] Failed to fetch detail XML for {date_key}: {e}")
            return None

        detail_text = resp.text
        detail_path = self.base_path / f"okiden_{date_key}.xml"
        detail_path.write_text(detail_text, encoding="utf-8")
        print(f"[OKIDEN] Saved detail XML → {detail_path.name}")
        return detail_path

    def run(self):
        master_path, master_text = self.fetch_master_xml()
        if not master_text:
            return

        date_keys = self.parse_date_keys(master_text)
        for key in date_keys:
            self.fetch_detail_xml(key)


if __name__ == "__main__":
    scraper = OkidenScraper()
    scraper.run()
