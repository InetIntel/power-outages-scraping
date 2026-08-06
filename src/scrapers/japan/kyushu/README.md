# Japan Kyushu Scraper Notes

Status: Draft generated from current repo evidence and validation-reviewed before packaging.

## Interpretation notes

- Line references such as `L###` are offsets from a generated per-folder Python inspection, not original source-file line numbers.
- Code terms such as `s3_path`, `Bucket`, and `list_objects_v2` may come from the current shared-volume `Uploader` shim and should not automatically be interpreted as active MinIO/S3 infrastructure.

## Registry

- Scraper ID: `japan_kyushu`
- Module: `japan.kyushu`
- Schedule: `0 1 * * *`
- Tags: `[japan, asia]`

## Files

- Scraper folder: `src/scrapers/japan/kyushu`
- Python files: `post_process.py`, `scrape.py`
- Dockerfile: generated at build time by `publish.sh` from the root templates (not committed)
- requirements.txt present: Yes
- requirements.txt empty: No

## Source / endpoint evidence

- `https://www.kyuden.co.jp/td_teiden/csv/RES{}_{}.csv`

- URL note: the observed URL includes parameterized template placeholders (`{}`). Verify runtime-expanded URLs before treating this as provider endpoint documentation.

## Observed implementation shape

- `class KyushuProcessor`
- `def __init__`
- `def parse_csv_file`
- `def run`
- `class KyushuScraper`
- `def __init__`
- `def fetch_for_date`
- `def fetch_last_7_days`

## Imports / dependencies observed

- `from datetime import datetime`
- `from datetime import datetime, timedelta`
- `from pathlib import Path`
- `from utils.upload import Uploader`
- `import csv`
- `import json`
- `import requests`

## Output behavior

Observed output-related lines from code inspection:

- `L4: import csv`
- `L5: import json`
- `L8: from utils.upload import Uploader`
- `L13: Processes Kyushu Electric Power outage CSVs (YYYYMMDDHHMM format) into structured JSON.`
- `L18: self.csv_dir = self.base_dir / "data" / "raw"`
- `L19: self.output_dir = self.base_dir / "data" / "processed"`
- `L22: def parse_csv_file(self, file_path):`
- `L26: reader = csv.reader(f)`
- `L32: start_raw,`
- `L33: end_raw,`
- `L42: start_dt = datetime.strptime(start_raw.strip(), "%Y%m%d%H%M")`
- `L43: end_dt = datetime.strptime(end_raw.strip(), "%Y%m%d%H%M")`
- `L48: start_time = start_raw.strip()`
- `L49: end_time = end_raw.strip()`
- `L74: uploader = Uploader("japan")`
- `L79: prefix = f"japan/kyushu/raw/{year}/{month}/"`
- `L80: listing = uploader.client.list_objects_v2(Bucket="japan", Prefix=prefix)`
- `L83: local_path = self.csv_dir / Path(key).name`
- `L84: uploader.download_file(key, str(local_path))`
- `L88: for csv_file in sorted(self.csv_dir.glob("*.csv")):`
- `L89: print(f"[PROCESS] Parsing {csv_file.name}")`
- `L90: entries = self.parse_csv_file(csv_file)`
- `L93: output_file = self.output_dir / "kyushu_power_outages.json"`
- `L95: json.dump(all_outages, f, ensure_ascii=False, indent=2)`
- `L99: # Upload processed file to shared volume`

Use neutral wording such as `observed output shape`, `processed provider-specific output`, and `current output behavior` unless direct evidence proves a stronger claim.

## Known risks / review notes

- No obvious risk keywords found by static scan.

## TODO / incomplete markers

- No TODO/TBD/FIXME/pass markers found by static scan.

## Runtime status

- Unknown — evidence needed unless a runtime validation report exists for this scraper.

## Documentation status

- This note is a generated draft and needs human review before being committed.
- Verify endpoint behavior, runtime output, and any provider-specific assumptions before treating this as final documentation.
