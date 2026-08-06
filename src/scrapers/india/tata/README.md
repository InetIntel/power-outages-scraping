# India Tata Scraper Notes

Status: Draft generated from current repo evidence and validation-reviewed before packaging.

## Interpretation notes

- Line references such as `L###` are offsets from a generated per-folder Python inspection, not original source-file line numbers.
- Code terms such as `s3_path`, `Bucket`, and `list_objects_v2` may come from the current shared-volume `Uploader` shim and should not automatically be interpreted as active MinIO/S3 infrastructure.

## Registry

- Scraper ID: `india_tata`
- Module: `india.tata`
- Schedule: `0 5 * * *`
- Tags: `[india, asia]`

## Files

- Scraper folder: `src/scrapers/india/tata`
- Python files: `post_process.py`, `scrape.py`
- Dockerfile: generated at build time by `publish.sh` from the root templates (not committed)
- requirements.txt present: Yes
- requirements.txt empty: No

## Source / endpoint evidence

- `https://customerportal.tatapower.com/TPCD/OuterOutage.aspx#`

## Observed implementation shape

- `class TataProcessor`
- `def __init__`
- `def create_folder`
- `def find_latest_raw_file`
- `def check_for_scrape_failure`
- `def parse`
- `def save`
- `def save_log`
- `def run`
- `class TataScraper`
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
- `from selenium.webdriver.support.ui import WebDriverWait`
- `import glob`
- `import json`
- `import os`
- `import time`
- `import traceback`

## Output behavior

Observed output-related lines from code inspection:

- `L5: import json`
- `L28: def find_latest_raw_file(self):`
- `L29: raw_folder = self.create_folder("raw")`
- `L30: today_file = glob.glob(os.path.join(raw_folder, f"*{self.today_str}.html"))`
- `L34: glob.glob(os.path.join(raw_folder, "*.html")),`
- `L41: raw_folder = self.create_folder("raw")`
- `L42: return os.path.exists(os.path.join(raw_folder, f"404_{self.today_str}.txt"))`
- `L46: soup = BeautifulSoup(f.read(), "html.parser")`
- `L78: folder = self.create_folder("processed")`
- `L80: folder, f"power_outages.IND.{self.provider}.processed.{self.today_str}.json"`
- `L83: json.dump(data, f, indent=2)`
- `L87: log_folder = self.create_folder("processed")`
- `L100: file_path = self.find_latest_raw_file()`
- `L102: print("No raw HTML file found.")`
- `L159: raw_folder = self.create_folder("raw")`
- `L189: html = driver.page_source`
- `L192: raw_folder,`
- `L193: f"power_outages.IND.{self.provider}.raw.{self.today_iso}.html",`
- `L196: f.write(html)`
- `L197: print(f"Saved raw outage HTML: {file_path}")`
- `L207: error_file = os.path.join(raw_folder, f"404_{self.today_iso}.txt")`

Use neutral wording such as `observed output shape`, `processed provider-specific output`, and `current output behavior` unless direct evidence proves a stronger claim.

## Known risks / review notes

- No obvious risk keywords found by static scan.

## TODO / incomplete markers

- `L219: pass`

## Runtime status

- Unknown — evidence needed unless a runtime validation report exists for this scraper.

## Documentation status

- This note is a generated draft and needs human review before being committed.
- Verify endpoint behavior, runtime output, and any provider-specific assumptions before treating this as final documentation.
