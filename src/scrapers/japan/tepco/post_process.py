from pathlib import Path
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json


class TEPCOProcessor:
    """
    Processor for Tokyo Electric Power Company (TEPCO) XML outage data.
    Combines the last 7 days of XML files into a single JSON file:
        power_outages.JP.tepco.processed.YYYY-MM-DD.json
    """

    def __init__(self):
        self.provider = "tepco"
        self.country_code = "JP"

    
        self.base_dir = Path(__file__).resolve().parent
        self.data_dir = self.base_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "processed").mkdir(parents=True, exist_ok=True)

        self.today = datetime.now()
        self.today_iso = self.today.strftime("%Y-%m-%d")

    def _get_raw_file_path(self, date: datetime):
        """Return path to the raw XML file for the given date."""
        date_str = date.strftime("%Y-%m-%d")
        filename = f"power_outages.{self.country_code}.{self.provider}.raw.{date_str}.xml"
        return self.data_dir / "raw" / filename

    def _get_output_path(self):
        """Single combined weekly JSON output file in data directory."""
        filename = f"power_outages.{self.country_code}.{self.provider}.processed.{self.today_iso}.json"
        return self.data_dir / "processed" / filename

    def _parse_outages(self, xml_content: str):
        """Parse one XML file into a list of outage dicts."""
        soup = BeautifulSoup(xml_content, "xml")
        outages = []

        selection = soup.find("停電表示選択", {"値": "５分以上の停電"})
        if not selection:
            return outages  # No data

        for block in selection.find_all("データ部"):
            start = block.find("発生日時")
            end = block.find("復旧日時")
            if not start or not end:
                continue

            prefecture = block.find("都県名").text if block.find("都県名") else ""
            city = block.find("市区町村名").text if block.find("市区町村名") else ""
            districts = [d.text for d in block.find_all("地区名")]
            houses_tag = block.find("停電軒数")
            reason_tag = block.find("停電理由")

            try:
                houses = int(houses_tag.text) if houses_tag else None
            except ValueError:
                houses = None

            outage = {
                "start": start.text,
                "end": end.text,
                "prefecture": prefecture,
                "city": city,
                "districts": districts,
                "houses_affected": houses,
                "reason": reason_tag.text if reason_tag else ""
            }

            outages.append(outage)

        return outages

    def run(self, days_back: int = 7):
        """Parse and combine the last `days_back` days of XML into one JSON file."""
        all_outages = []

        for i in range(days_back + 1):
            date = self.today - timedelta(days=i)
            raw_path = self._get_raw_file_path(date)
            if not raw_path.exists():
                print(f"Missing raw XML for {date.strftime('%Y-%m-%d')} ({raw_path.name})")
                continue

            try:
                xml_content = raw_path.read_text(encoding="utf-8")
                outages = self._parse_outages(xml_content)
                all_outages.extend(outages)
                print(f"[TEPCO] Parsed {raw_path.name} → {len(outages)} outages")
            except Exception as e:
                print(f"Error reading {raw_path.name}: {e}")

        # Save combined weekly JSON
        output_path = self._get_output_path()
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_outages, f, ensure_ascii=False, indent=2)

        print(f"\nSaved weekly TEPCO outages → {output_path.name} ({len(all_outages)} total)")
        return output_path


if __name__ == "__main__":
    processor = TEPCOProcessor()
    processor.run()
