# India Bses Rajdhani Scraper Notes

Status: Draft generated from current repo evidence and validation-reviewed before packaging.

## Interpretation notes

- Line references such as `L###` are offsets from a generated per-folder Python inspection, not original source-file line numbers.
- Code terms such as `s3_path`, `Bucket`, and `list_objects_v2` may come from the current shared-volume `Uploader` shim and should not automatically be interpreted as active MinIO/S3 infrastructure.

## Registry

- Scraper ID: `india_bses_rajdhani`
- Module: `india.bses_rajdhani`
- Schedule: `0 5 * * *`
- Tags: `[india, asia]`

## Files

- Scraper folder: `src/scrapers/india/bses_rajdhani`
- Python files: `post_process.py`, `scrape.py`
- Dockerfile: generated at build time by `publish.sh` from the root templates (not committed)
- requirements.txt present: Yes
- requirements.txt empty: No

## Source / endpoint evidence

- `https://www.bsesdelhi.com/web/brpl/maintenance-outage-schedule`

## Observed implementation shape

- `class BSESRajdhaniProcessor`
- `def __init__`
- `def create_folder`
- `def find_latest_raw_file`
- `def parse_html`
- `def save_json`
- `def process`
- `class BSESRajdhani`
- `def __init__`
- `def create_folder`
- `def get_chrome_driver`
- `def scrape`

## Imports / dependencies observed

- `from bs4 import BeautifulSoup`
- `from datetime import datetime`
- `from selenium import webdriver`
- `from selenium.webdriver.chrome.options import Options`
- `from selenium.webdriver.chrome.service import Service`
- `from selenium.webdriver.common.by import By`
- `from selenium.webdriver.support import expected_conditions as EC`
- `from selenium.webdriver.support.ui import WebDriverWait, Select`
- `import glob`
- `import json`
- `import os`
- `import time`
- `import traceback`

## Output behavior

Observed output-related lines from code inspection:

- `L5: import json`
- `L35: def find_latest_raw_file(self):`
- `L36: raw_folder = self.create_folder("raw")`
- `L37: today_file = glob.glob(os.path.join(raw_folder, f"*{self.today_iso}.html"))`
- `L41: glob.glob(os.path.join(raw_folder, "*.html")),`
- `L47: def parse_html(self, html_path):`
- `L48: with open(html_path, "r", encoding="utf-8") as f:`
- `L49: soup = BeautifulSoup(f.read(), "html.parser")`
- `L101: def save_json(self, data):`
- `L102: folder = self.create_folder("processed")`
- `L103: filename = f"power_outages.IND.{self.provider}.processed.{self.today_iso}.json"`
- `L106: json.dump(data, f, indent=2, ensure_ascii=False)`
- `L107: print(f"Saved processed JSON: {path}")`
- `L111: raw_folder = self.create_folder("raw")`
- `L113: os.path.join(raw_folder, f"404_{self.today_iso}.txt")`
- `L116: raw_file = self.find_latest_raw_file()`
- `L117: if raw_file:`
- `L118: print(f"Processing file: {raw_file}")`
- `L119: parsed_data = self.parse_html(raw_file)`
- `L120: self.save_json(parsed_data)`
- `L122: print("No raw file found.")`
- `L125: self.create_folder("processed"), f"no_data_found.{self.today_iso}.log"`
- `L129: f"No outage schedule found for {self.today_iso}. See {os.path.basename(not_found_files[0])} in raw folder."`
- `L191: raw_folder = self.create_folder("raw")`
- `L212: os.path.join(raw_folder, f"404_{self.today_iso}.txt"),`

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
