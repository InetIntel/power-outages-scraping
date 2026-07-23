# Thailand Mea Scraper Notes

Status: Draft generated from current repo evidence and validation-reviewed before packaging.

## Interpretation notes

- Line references such as `L###` are offsets from a generated per-folder Python inspection, not original source-file line numbers.
- Code terms such as `s3_path`, `Bucket`, and `list_objects_v2` may come from the current shared-volume `Uploader` shim and should not automatically be interpreted as active MinIO/S3 infrastructure.

## Registry

- Scraper ID: `thailand_mea`
- Module: `thailand.mea`
- Schedule: `0 2 * * *`
- Tags: `[thailand, asia]`

## Files

- Scraper folder: `src/scrapers/thailand/mea`
- Python files: `post_process.py`, `scrape.py`
- Dockerfile: generated at build time by `publish.sh` from the root templates (not committed)
- requirements.txt present: Yes
- requirements.txt empty: No

## Source / endpoint evidence

- `https://www.mea.or.th/en/public-relations/power-outage-notifications/news`
- `https://www.mea.or.th{url}`

- URL note: `https://www.mea.or.th{url}` is an observed base-plus-template expression, not a directly fetchable static URL literal.

## Observed implementation shape

- `class Process_MEA`
- `def __init__`
- `def download_raw_files`
- `def clean_text`
- `def parse_html_content`
- `def parse_date`
- `def convert_to_24h`
- `def create_outage_entry`
- `def get_data`
- `def check_folder`
- `def save_json`
- `def run`
- `class MEA_Thailand`
- `def __init__`
- `def check_folder`
- `async def fetch_listing_page`
- `async def fetch_announcement`
- `def extract_announcement_urls`
- `async def fetch_all`
- `async def scrape`

Note: the original static scan omitted the four `async def` methods above (same pattern-matching gap found in `cameroon` and `nigeria/ikeja`) — `fetch_all` is the orchestrator that pages through the listing, fans out `fetch_announcement` calls concurrently, and uploads results; `scrape` is the `__main__` entry point.

## Imports / dependencies observed

- `from bs4 import BeautifulSoup`
- `from datetime import datetime`
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
- `L36: local_folder = f"./thailand/mea/raw/{self.year}/{self.month}"`
- `L39: if not self.uploader:`
- `L40: print("Uploader not initialized, will use local files only")`
- `L44: s3_prefix = f"thailand/mea/raw/{self.year}/{self.month}/"`
- `L48: response = self.uploader.client.list_objects_v2(`
- `L56: downloaded_count = 0`
- `L71: self.uploader.download_file(file_key, local_file_path)`
- `L72: downloaded_count += 1`
- `L74: print(f"Error downloading {file_name}: {e}")`
- `L76: print(f"Downloaded {downloaded_count} HTML files from S3")`
- `L78: print(f"Error listing/downloading files: {e}")`
- `L88: text_raw = element.get_text()`
- `L90: text = text_raw.replace("\xa0", " ")`
- `L94: def parse_html_content(self, html_content, announcement_id):`
- `L95: """Parse HTML content to extract power outage information"""`
- `L96: soup = BeautifulSoup(html_content, "html.parser")`
- `L266: """Load individual HTML files and process them"""`
- `L267: folder = f"./thailand/mea/raw/{self.year}/{self.month}"`

Use neutral wording such as `observed output shape`, `processed provider-specific output`, and `current output behavior` unless direct evidence proves a stronger claim.

## Known risks / review notes

- No obvious risk keywords found by static scan.

## TODO / incomplete markers

- `L247: pass` — `scrape.py`'s `fetch_all()`, `except Exception: pass` around the S3 upload loop; silently swallows any upload failure.
- `L542: pass` — `post_process.py`'s `create_outage_entry()`, `if end_datetime < start_datetime: pass`. The comment above it says "Handle case where end time is next day," but the handler is a no-op — nothing adds a day to `end_datetime`. The resulting negative duration is then clamped to `0.00` by `max(duration, 0)` in the returned record, so overnight outages silently get a `duration_(hours)` of `0.00` instead of the correct value.

## Runtime status

- Unknown — evidence needed unless a runtime validation report exists for this scraper.

## Documentation status

- This note is a generated draft and needs human review before being committed.
- Verify endpoint behavior, runtime output, and any provider-specific assumptions before treating this as final documentation.
