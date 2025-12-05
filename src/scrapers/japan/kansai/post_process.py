from pathlib import Path
from datetime import datetime, timedelta, timezone
import json


class KansaiProcessor:
    """
    Processor for Kansai Transmission and Distribution outage history data.
    Reads a single raw JSON file and outputs a processed summary file:
        power_outages.JP.kansai.processed.YYYY-MM-DD.json
    """

    def __init__(self):
        self.provider = "kansai"
        self.country_code = "JP"

        # Local path (change to your local dir if needed)
        self.data_dir = Path(__file__).resolve().parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "processed").mkdir(parents=True, exist_ok=True)

        # Japan Standard Time (UTC+9)
        self.JST = timezone(timedelta(hours=9))
        self.today = datetime.now(self.JST)
        self.today_iso = self.today.strftime("%Y-%m-%d")

    def _get_raw_file_path(self):
        """Path to the raw Kansai JSON file."""
        filename = f"power_outages.{self.country_code}.{self.provider}.raw.{self.today_iso}.json"
        return self.data_dir / "raw" / filename

    def _get_output_file_path(self):
        """Path to the processed output JSON file."""
        filename = f"power_outages.{self.country_code}.{self.provider}.processed.{self.today_iso}.json"
        return self.data_dir / "processed" / filename

    def _parse_outages(self, raw_data):
        """Parse Kansai JSON data into a flattened structured list."""
        all_outages = []

        entries = raw_data.get("entries", {}).get("list", [])
        if not entries:
            print("No outage entries found.")
            return all_outages

        for date_entry in entries:
            date_str = date_entry.get("date")
            for record in date_entry.get("list", []):
                off_time = record.get("offdatetime")
                repair_time = record.get("repairtime")
                reason = record.get("offcause")
                total_houses = record.get("number") or 0

                # Nested area breakdown
                for pref in record.get("areas", []):
                    pref_name = pref.get("name", "")
                    for city in pref.get("children", []):
                        city_name = city.get("name", "")
                        for subarea in city.get("children", []):
                            sub_name = subarea.get("name", "")
                            houses = subarea.get("number") or 0

                            start_dt, end_dt, duration = None, None, None
                            try:
                                start_dt = datetime.strptime(off_time, "%Y-%m-%d %H:%M")
                                start_dt = start_dt.replace(tzinfo=self.JST)
                            except Exception:
                                pass
                            try:
                                end_dt = datetime.strptime(repair_time, "%Y-%m-%d %H:%M")
                                end_dt = end_dt.replace(tzinfo=self.JST)
                            except Exception:
                                pass

                            if start_dt and end_dt:
                                duration = round((end_dt - start_dt).total_seconds() / 3600, 2)

                            outage = {
                                "date": date_str,
                                "start": off_time,
                                "end": repair_time,
                                "duration_(hours)": duration,
                                "prefecture": pref_name,
                                "city": city_name,
                                "area": sub_name,
                                "houses_affected": houses,
                                "total_event_houses": total_houses,
                                "reason": reason,
                            }

                            all_outages.append(outage)

        return all_outages

    def run(self):
        """Run processor to parse and save processed JSON."""
        input_path = self._get_raw_file_path()
        if not input_path.exists():
            print(f"Raw Kansai JSON not found: {input_path}")
            return None

        with open(input_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        outages = self._parse_outages(raw_data)
        output_path = self._get_output_file_path()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(outages, f, ensure_ascii=False, indent=2)

        print(f"\nProcessed {len(outages)} outages → {output_path.name}")
        return output_path


if __name__ == "__main__":
    processor = KansaiProcessor()
    processor.run()
