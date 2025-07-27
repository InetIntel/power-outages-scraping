import os
import json
import pandas as pd
from datetime import datetime
import glob

class Process_Npp:
    def __init__(self, year, month, date, file_path, report_name):
        self.year = year
        self.month = month
        self.date = date
        self.file_path = file_path
        self.report_name = report_name
        self.output_path = f"/data/india/npp/processed/{year}/{month}"
        os.makedirs(self.output_path, exist_ok=True)

    def parse_datetime(self, value):
        try:
            return datetime.strptime(value, "%d/%m/%Y %H:%M")
        except Exception as e:
            print(f"Bad start datetime: {value}")
            return None

    def read_file(self):
        try:
            df = pd.read_excel(self.file_path, engine="xlrd", header=None, skiprows=3)
        except Exception as e:
            print(f"Failed to read Excel: {e}")
            return []

        outage = []

        for _, row in df.iterrows():
            try:
                start_col = str(row[8]).strip()
                if " " not in start_col or "/" not in start_col:
                    continue  # skip bad row

                start_date_str, start_time_str = start_col.split(" ", 1)
                start_date = datetime.strptime(start_date_str.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
                start_time = datetime.strptime(start_time_str.strip(), "%H:%M")

                data = {
                    "country": "India",
                    "start": f"{start_date}_{start_time.strftime('%H-%M-%S')}",
                    "event_category": str(row[10]).strip() if not pd.isna(row[10]) else "unknown",
                    "area_affected": {
                        str(row[0]).strip() if not pd.isna(row[0]) else "unknown":
                            str(row[2]).strip() if not pd.isna(row[2]) else "unknown"
                    }
                }

                # Optional end time
                if not pd.isna(row[9]) and " " in str(row[9]):
                    end_col = str(row[9]).strip()
                    end_date_str, end_time_str = end_col.split(" ", 1)
                    end_date = datetime.strptime(end_date_str.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
                    end_time = datetime.strptime(end_time_str.strip(), "%H:%M")
                    data["end"] = f"{end_date}_{end_time.strftime('%H-%M-%S')}"
                    start_dt = datetime.strptime(start_col, "%d/%m/%Y %H:%M")
                    end_dt = datetime.strptime(end_col, "%d/%m/%Y %H:%M")
                    duration_minutes = round((end_dt - start_dt).total_seconds() / 60)
                    data["duration_(minutes)"] = duration_minutes

                outage.append(data)

            except Exception as e:
                print(f"Bad row: {e}")
                continue

        return outage



    def save(self, data):
        filename = f"power_outages.IND.npp.processed.{self.date}.{self.report_name}.json"
        path = os.path.join(self.output_path, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved: {path} ({len(data)} records)")

    def run(self):
        data = self.read_file()
        self.save(data)


def detect_and_run():
    # Look under full directory tree
    search_pattern = "/data/india/npp/raw/*/*/power_outages.IND.npp.raw.*.xls"
    files = sorted(glob.glob(search_pattern), key=os.path.getmtime, reverse=True)

    if not files:
        print(f"No raw files found under: {search_pattern}")
        return

    for file_path in files:
        base = os.path.basename(file_path)
        parts = base.split(".")
        if len(parts) < 5:
            print(f"Skipping malformed filename: {base}")
            continue

        try:
            date_str = parts[4]  # e.g. 2025-07-24
            report_name = parts[5].replace(".xls", "")
            year, month, _ = date_str.split("-")
        except Exception as e:
            print(f"Failed to parse filename: {base} ({e})")
            continue

        processor = Process_Npp(year, month, date_str, file_path, report_name)
        processor.run()


if __name__ == "__main__":
    detect_and_run()
