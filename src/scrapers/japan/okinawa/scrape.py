import requests
from pathlib import Path
import xml.etree.ElementTree as ET
import time

class OkidenScraper:
    MASTER_URL = "https://www.okidenmail.jp/bosai/xml/history_normal.xml"
    DETAIL_URL = "https://www.okidenmail.jp/bosai/api/xml_map2.php"

    def __init__(self):
        self.base_path = Path(__file__).resolve().parent / "data" / "raw"
        self.base_path.mkdir(parents=True, exist_ok=True)

    def fetch_master(self):
        ts = int(time.time() * 1000)
        url = f"{self.MASTER_URL}?_={ts}"
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; outage-scraper/1.0)",
            "Referer": "https://www.okidenmail.jp/bosai/info2/"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        xml_text = resp.text

        master_path = self.base_path / f"okiden_master_{ts}.xml"
        master_path.write_text(xml_text, encoding="utf-8")
        print("Saved master XML →", master_path)
        return master_path, xml_text

    def parse_master_for_keys(self, xml_text):
        """Extract date_key or similar IDs from master XML."""
        root = ET.fromstring(xml_text)
        keys = []
        # This depends on actual XML structure — adjust tag names as needed
        for elem in root.findall(".//date_key"):
            key = elem.text.strip()
            keys.append(key)
        return keys

    def fetch_detail(self, date_key: str):
        ts = int(time.time() * 1000)
        url = f"{self.DETAIL_URL}?date_key={date_key}&_={ts}"
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; outage-scraper/1.0)",
            "Referer": "https://www.okidenmail.jp/bosai/info2/"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        xml_text = resp.text

        if not xml_text.strip().startswith("<?xml"):
            print(f"[WARN] detail for {date_key} did not return XML")
            return None

        detail_path = self.base_path / f"okiden_{date_key}.xml"
        detail_path.write_text(xml_text, encoding="utf-8")
        print("Saved detail XML →", detail_path)
        return detail_path

    def run(self):
        master_path, xml_text = self.fetch_master()
        keys = self.parse_master_for_keys(xml_text)
        print("Found keys:", keys)

        for key in keys:
            try:
                self.fetch_detail(key)
                time.sleep(1)  # polite delay
            except Exception as e:
                print(f"[ERROR] fetching detail for {key}: {e}")


if __name__ == "__main__":
    scraper = OkidenScraper()
    scraper.run()
