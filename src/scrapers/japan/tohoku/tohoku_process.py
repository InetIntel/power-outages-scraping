from pathlib import Path
from datetime import datetime
import json
from pathlib import Path


class TohokuProcessor:
    """
    Processor for Tohoku Electric Power Company (東北電力) outage JSON data.
    Reads a single raw JSON file and outputs a processed summary file:
        power_outages.JP.tohoku.processed.YYYY-MM-DD.json
    """

    def __init__(self):
        self.provider = "tohoku"
        self.country_code = "JP"

        # Base and data paths
        self.data_dir = Path(__file__).resolve().parent / "data" 
        # self.data_dir = Path("/dagu/data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "processed").mkdir(parents=True, exist_ok=True)


        # Date references
        self.today = datetime.now()
        self.today_iso = self.today.strftime("%Y-%m-%d")

    def _get_raw_file_path(self):
        """Path to the raw Tohoku JSON file."""
        filename = f"power_outages.{self.country_code}.{self.provider}.raw.{self.today_iso}.json"
        return self.data_dir / "raw" / filename

    def _get_output_file_path(self):
        """Path to the processed output JSON file."""
        filename = f"power_outages.{self.country_code}.{self.provider}.processed.{self.today_iso}.json"
        return self.data_dir / "processed" / filename

    def _parse_outages(self, raw_data):
        """Extract outages from JSON into a consistent structured list."""
        all_outages = []

        entries = raw_data.get("entries", [])
        if not entries:
            print("No entries found in Tohoku JSON data.")
            return all_outages

        for entry in entries:
            details = entry.get("details", [])
            if not details:
                continue

            for d in details:
                start_time = d.get("time")
                end_time = d.get("recovery_time")
                pref = d.get("pref_name")
                city_area = d.get("name", "")
                houses = d.get("count", 0)
                reason = d.get("reason", "")

                # Try parsing the Japanese-style time formats like "10月12日 05:19"
                start_dt = None
                end_dt = None
                duration = None

                try:
                    # Add current year if missing
                    year = self.today.year
                    start_dt = datetime.strptime(f"{year}年{start_time}", "%Y年%m月%d日 %H:%M")
                except Exception:
                    pass

                try:
                    year = self.today.year
                    end_dt = datetime.strptime(f"{year}年{end_time}", "%Y年%m月%d日 %H:%M")
                except Exception:
                    pass

                if start_dt and end_dt:
                    duration = round((end_dt - start_dt).total_seconds() / 3600, 2)

                outage = {
                    "start": start_time,
                    "end": end_time,
                    "duration_(hours)": duration,
                    "prefecture": pref,
                    "location": city_area,
                    "houses_affected": houses,
                    "reason": reason.strip(),
                }

                all_outages.append(outage)

        return all_outages

    def run(self):
        """Run processor to parse and save processed JSON."""
        input_path = self._get_raw_file_path()
        if not input_path.exists():
            print(f"Raw Tohoku JSON not found: {input_path}")
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
    processor = TohokuProcessor()
    processor.run()
