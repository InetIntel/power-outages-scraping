import csv
import json
from pathlib import Path
from datetime import datetime

class KyushuProcessor:
    """
    Processes Kyushu Electric Power outage CSVs (YYYYMMDDHHMM format) into structured JSON.
    """
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.csv_dir = self.base_dir / "data" / "raw"
        self.output_dir = self.base_dir / "data" / "processed"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def parse_csv_file(self, file_path):
        outages = []

        with open(file_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 7:
                    continue  # skip invalid rows

                start_raw, end_raw, city, area, households_total, households_affected, reason = row

                try:
                    start_dt = datetime.strptime(start_raw.strip(), "%Y%m%d%H%M")
                    end_dt = datetime.strptime(end_raw.strip(), "%Y%m%d%H%M")
                    start_time = start_dt.strftime("%Y-%m-%d %H:%M")
                    end_time = end_dt.strftime("%Y-%m-%d %H:%M")
                    duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
                except Exception:
                    start_time = start_raw.strip()
                    end_time = end_raw.strip()
                    duration_minutes = None

                city = city.strip()
                area = area.strip()
                households_affected = households_affected.strip()
                reason = reason.strip()

                if not city or city == "―":
                    continue

                outage_entry = {
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration_minutes": duration_minutes,
                    "reason": reason,
                    "households_affected": households_affected,
                    "areas": [
                        {"prefecture": "Kyushu", "city": city, "area": area}
                    ]
                }

                outages.append(outage_entry)

        return outages

    def run(self):
        all_outages = []

        for csv_file in sorted(self.csv_dir.glob("*.csv")):
            print(f"[PROCESS] Parsing {csv_file.name}")
            entries = self.parse_csv_file(csv_file)
            all_outages.extend(entries)

        output_file = self.output_dir / "kyushu_power_outages.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_outages, f, ensure_ascii=False, indent=2)

        print(f"\nParsed {len(all_outages)} outages → {output_file}")
        return output_file


if __name__ == "__main__":
    processor = KyushuProcessor()
    processor.run()
