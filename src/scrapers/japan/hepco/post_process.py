# processor_hepco.py
import json
import re
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup


class HEPCOProcessor:
    def __init__(self):
        self.provider = "hepco"
        self.country = "japan"
        self.base_path = Path(__file__).resolve().parent / "data"   

        # Use today's date unless overridden
        target_date = datetime.now()
        self.today_iso = target_date.strftime("%Y-%m-%d")
        self.today_jp = target_date.strftime("%Y/%m/%d")
        self.year = target_date.strftime("%Y")
        self.month = target_date.strftime("%m")
        self.day = target_date.strftime("%d")

        # File naming convention
        self.raw_filename = f"power_outages.JP.{self.provider}.raw.{self.today_iso}.html"
        self.processed_filename = f"power_outages.JP.{self.provider}.processed.{self.today_iso}.json"

        # Path setup
        self.raw_path = Path(self.base_path) / "raw" / self.raw_filename
        self.output_path = Path(self.base_path) / "processed" / self.processed_filename


    # === CORE PARSING ===
    def parse_raw_outages(self, html: str):
        """Extract raw outage entries using regex patterns."""
        soup = BeautifulSoup(html, "html.parser")

        container = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", id="content")
            or soup.body
        )

        text = container.get_text("\n", strip=True)
        text = re.sub(r"\n{2,}", "\n", text)

        pattern = re.compile(
            r"(\d{4}/\d{2}/\d{2})\s*(\d{1,2}:\d{2})\s*↓\s*"
            r"(\d{4}/\d{2}/\d{2})\s*(\d{1,2}:\d{2})\s*"
            r"(.+?)\s+約?(\d+)[戸]\s+(.+?)(?=(?:\d{4}/\d{2}/\d{2}\s*\d{1,2}:\d{2})|$)",
            re.S
        )

        raw_records = []
        for m in pattern.finditer(text):
            start_d, start_t, end_d, end_t, area, hh, cause = m.groups()
            raw_records.append({
                "start_date": start_d,
                "start_time": start_t,
                "end_date": end_d,
                "end_time": end_t,
                "area_text": area.strip(),
                "households": hh,
                "cause_text": cause.strip(),
            })

        print(f"Extracted {len(raw_records)} raw outage records")
        return raw_records


    def process_records(self, raw_records):
        """Convert raw records into standardized outage entries."""
        processed = []
        for r in raw_records:
            try:
                start_dt = datetime.strptime(f"{r['start_date']} {r['start_time']}", "%Y/%m/%d %H:%M")
                end_dt = datetime.strptime(f"{r['end_date']} {r['end_time']}", "%Y/%m/%d %H:%M")
                duration = round((end_dt - start_dt).total_seconds() / 3600, 2)
            except Exception:
                start_dt, end_dt, duration = None, None, None

            processed.append({
                "start": start_dt.strftime("%Y-%m-%d_%H-%M-%S") if start_dt else None,
                "end": end_dt.strftime("%Y-%m-%d_%H-%M-%S") if end_dt else None,
                "duration_(hours)": duration,
                "event_category": "unplanned_outage",
                "country": "Japan",
                "areas_affected": [r.get("area_text")],
                "households": int(r.get("households", "0") or 0),
                "cause": r.get("cause_text"),
            })
        return processed


    def run(self):
        """Main entry point: load HTML → parse → process → save JSON."""
        if not self.raw_path.exists():
            raise FileNotFoundError(f"Raw HTML file not found: {self.raw_path}")

        html = self.raw_path.read_text(encoding="utf-8")
        raw_records = self.parse_raw_outages(html)
        processed = self.process_records(raw_records)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        self.output_path.write_text(json.dumps(processed, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Processed {len(processed)} records → {self.output_path}")


if __name__ == "__main__":
    processor = HEPCOProcessor()
    processor.run()
