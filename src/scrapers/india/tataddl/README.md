# India Tataddl Scraper Notes

Status: Draft generated from current repo evidence and validation-reviewed before packaging.

## Interpretation notes

- Line references such as `L###` are offsets from a generated per-folder Python inspection, not original source-file line numbers.
- Code terms such as `s3_path`, `Bucket`, and `list_objects_v2` may come from the current shared-volume `Uploader` shim and should not automatically be interpreted as active MinIO/S3 infrastructure.

## Registry

- Scraper ID: `india_tataddl`
- Module: `india.tataddl`
- Schedule: `0 5 * * *`
- Tags: `[india, asia]`

## Files

- Scraper folder: `src/scrapers/india/tataddl`
- Python files: `post_process.py`, `scrape.py`
- Dockerfile: generated at build time by `publish.sh` from the root templates (not committed)
- requirements.txt present: Yes
- requirements.txt empty: No

## Source / endpoint evidence

- `https://tatapower-ddl.com/scheduleoutage/119/customers/scheduled-outage`

## Observed implementation shape

- `class Process_tataddl`
- `def __init__`
- `def create_folder`
- `def find_latest_raw_file`
- `def check_for_scrape_failure`
- `def parse`
- `def save`
- `def save_log`
- `def run`
- `class Tataddl`
- `def __init__`
- `def create_folder`
- `def get_chrome_driver`
- `def fetch`
- `def scrape`

## Imports / dependencies observed

- `from bs4 import BeautifulSoup`
- `from datetime import datetime`
- `from selenium import webdriver`
- `from selenium.webdriver.chrome.options import Options`
- `from selenium.webdriver.chrome.service import Service`
- `from selenium.webdriver.common.by import By`
- `from selenium.webdriver.support import expected_conditions as EC`
- `from selenium.webdriver.support.ui import Select`
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
- `L72: folder = self.create_folder("processed")`
- `L74: folder, f"power_outages.IND.{self.provider}.processed.{self.today_str}.json"`
- `L77: json.dump(data, f, indent=2)`
- `L81: log_folder = self.create_folder("processed")`
- `L94: file_path = self.find_latest_raw_file()`
- `L96: print("No raw HTML file found.")`
- `L105: # raw_dir = os.path.join(os.path.dirname(__file__), "raw", "2025", "09")`
- `L106: # file_name = "power_outages.IND.tataddl.raw.2025-09-26.html"`
- `L107: # file = os.path.join(raw_dir, file_name)`
- `L135: # import json`
- `L192: raw_folder = self.create_folder("raw")`
- `L206: html = driver.page_source`
- `L208: raw_folder,`
- `L209: f"power_outages.IND.{self.provider}.raw.{self.today_iso}.html",`
- `L212: f.write(html)`
- `L213: print(f"Saved raw outage HTML: {file_path}")`
- `L222: error_file = os.path.join(raw_folder, f"404_{self.today_iso}.txt")`

Use neutral wording such as `observed output shape`, `processed provider-specific output`, and `current output behavior` unless direct evidence proves a stronger claim.

## Known risks / review notes

- No obvious risk keywords found by static scan (security-pattern scan only; see functional notes below).
- `get_chrome_driver()` builds a `Service("/usr/bin/chromedriver")` (and does so twice, redundantly) but never passes it to `webdriver.Chrome(options=options)` — unlike every sibling India Selenium scraper (bses_rajdhani, bses_yamuna, mahavitaran, tata), which all pass `service=service`. The explicit chromedriver path is silently unused here; whether Selenium still finds a working driver depends on its auto-discovery behavior in the container.
- `fetch()` duplicates `scrape()`'s logic using non-headless `webdriver.ChromeOptions()` with `detach=True` (meant for local interactive debugging) and is never called from `scrape()` or `__main__` — it is dead code.

## TODO / incomplete markers

- `L234: pass`

## Runtime status

- Unknown — evidence needed unless a runtime validation report exists for this scraper.

## Documentation status

- This note is a generated draft and needs human review before being committed.
- Verify endpoint behavior, runtime output, and any provider-specific assumptions before treating this as final documentation.
