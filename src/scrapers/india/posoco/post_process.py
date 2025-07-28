import os
import json
import glob


def detect_and_run():
    search_pattern = "/data/india/posoco/raw/*/*/power_outages.IND.posoco.raw.*.pdf"
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
            date_str = parts[4]  # e.g. 2025-07
            year, month = date_str.split("-")
        except Exception as e:
            print(f"Failed to parse filename: {base} ({e})")
            continue

        # Placeholder data
        data = {
            "country": "India",
            "source": "POSOCO",
            "report_date": date_str,
            "notes": "PDF parsing not yet implemented",
        }

        output_dir = f"/data/india/posoco/processed/{year}/{month}"
        os.makedirs(output_dir, exist_ok=True)
        out_file = os.path.join(output_dir, f"power_outages.IND.posoco.processed.{date_str}.json")

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Saved: {out_file}")


if __name__ == "__main__":
    detect_and_run()
