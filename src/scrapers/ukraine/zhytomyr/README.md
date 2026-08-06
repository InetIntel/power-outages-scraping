# Ukraine Zhytomyr Scraper Notes

Status: Draft generated from current repo evidence and validation-reviewed before packaging.

## Interpretation notes

- Line references such as `L###` are offsets from a generated per-folder Python inspection, not original source-file line numbers.
- Code terms such as `s3_path`, `Bucket`, and `list_objects_v2` may come from the current shared-volume `Uploader` shim and should not automatically be interpreted as active MinIO/S3 infrastructure.

## Registry

- Scraper ID: `ukraine_zhytomyr`
- Module: `ukraine.zhytomyr`
- Schedule: `0 */6 * * *`
- Tags: `[ukraine, europe]`

## Files

- Scraper folder: `src/scrapers/ukraine/zhytomyr`
- Python files: `post_process.py`, `scrape.py`
- Dockerfile: generated at build time by `publish.sh` from the root templates (not committed)
- requirements.txt present: Yes
- requirements.txt empty: No

## Source / endpoint evidence

- `https://www.ztoe.com.ua/unhooking-search.php`

## Observed implementation shape

- `class Process_Zhytomyr`
- `def __init__`
- `def download_raw_files`
- `def parse_html_content`
- `def extract_outage_info`
- `def get_data`
- `def check_folder`
- `def save_json`
- `def run`
- `class Zhytomyr`
- `def __init__`
- `def check_folder`
- `async def fetch_single`
- `async def fetch_all`
- `async def scrape`

Note: the original static scan omitted the three `async def` methods above (same pattern-matching gap found in `cameroon`, `nigeria/ikeja`, `thailand/mea`, `ukraine/cherkasy`, and `ukraine/khmelnytsky`) — `fetch_all` fans out `fetch_single` across all 17 `rem_id`s concurrently and is where the inline post-processing call happens (see risk note below); `scrape` is the `__main__` entry point.

## Imports / dependencies observed

- `from bs4 import BeautifulSoup`
- `from datetime import datetime`
- `from post_process import Process_Zhytomyr`
- `from utils.upload import Uploader`
- `import asyncio`
- `import httpx`
- `import json`
- `import os`
- `import re`
- `import sys`

## Output behavior

Observed output-related lines from code inspection:

- `L4: import json`
- `L9: from utils.upload import Uploader`
- `L20: self.uploader = Uploader(self.bucket_name)`
- `L22: print(f"error initializing uploader: {e}")`
- `L23: self.uploader = None`
- `L25: def download_raw_files(self, date=None):`
- `L26: """Download all individual HTML files from S3"""`
- `L36: local_folder = f"./ukraine/zhytomyr/raw/{self.year}/{self.month}"`
- `L39: if not self.uploader:`
- `L40: print("Warning: uploader not initialized, will use local files only")`
- `L43: # List of rem_ids to download`
- `L64: downloaded_count = 0`
- `L66: file_name = f"power_outages.UA.zhytomyr.raw.{date}.{rem_id}.html"`
- `L67: s3_path = f"ukraine/zhytomyr/raw/{self.year}/{self.month}/{file_name}"`
- `L76: self.uploader.download_file(s3_path, local_file_path)`
- `L77: downloaded_count += 1`
- `L81: print(f"Error downloading {file_name}: {e}")`
- `L83: print(f"Downloaded {downloaded_count} HTML files from S3")`
- `L85: def parse_html_content(self, html_content):`
- `L86: """Parse HTML content to extract power outage information"""`
- `L87: soup = BeautifulSoup(html_content, "html.parser")`
- `L202: """Load individual HTML files and process them"""`
- `L203: folder = f"./ukraine/zhytomyr/raw/{self.year}/{self.month}"`
- `L233: html_file = f"power_outages.UA.zhytomyr.raw.{self.today}.{rem_id}.html"`
- `L234: html_path = os.path.join(folder, html_file)`

Use neutral wording such as `observed output shape`, `processed provider-specific output`, and `current output behavior` unless direct evidence proves a stronger claim.

## Known risks / review notes

- No obvious risk keywords found by static scan. (Unlike `ukraine/cherkasy` and `ukraine/khmelnytsky`, this scraper's `httpx.AsyncClient(timeout=30.0)` does not set `verify=False` — no TLS-verification bypass here.)
- **Processing runs twice per Airflow execution**, same pattern as `ukraine/cherkasy` and `ukraine/khmelnytsky`. `scrape.py`'s `fetch_all()` uploads each `rem_id`'s raw HTML, then directly instantiates `Process_Zhytomyr(...).run()` inline (lines 137-142) — i.e. the `scrape` task already performs the full scrape → parse → upload-processed pipeline. The separate `post_process` Airflow task then runs `post_process.py`'s own `__main__`, which re-downloads the same raw files, re-parses them, and re-uploads the (identical) processed JSON. Idempotent, not incorrect, but duplicated work.

## TODO / incomplete markers

- `L197: pass`

## Runtime status

- Unknown — evidence needed unless a runtime validation report exists for this scraper.

## Documentation status

- This note is a generated draft and needs human review before being committed.
- Verify endpoint behavior, runtime output, and any provider-specific assumptions before treating this as final documentation.
