# Cameroon Scraper Notes

Status: Draft generated from current repo evidence and validation-reviewed before packaging.

## Interpretation notes

- Line references such as `L###` are offsets from a generated per-folder Python inspection, not original source-file line numbers.
- Code terms such as `s3_path`, `Bucket`, and `list_objects_v2` may come from the current shared-volume `Uploader` shim and should not automatically be interpreted as active MinIO/S3 infrastructure.

## Registry

- Scraper ID: `cameroon`
- Module: `cameroon`
- Schedule: `0 8 * * *`
- Tags: `[cameroon, africa]`

## Files

- Scraper folder: `src/scrapers/cameroon`
- Python files: `post_process.py`, `scrape.py`
- Dockerfile: generated at build time by `publish.sh` from the root templates (not committed)
- requirements.txt present: Yes
- requirements.txt empty: No

## Source / endpoint evidence

- `https://alert.eneo.cm/ajaxOutage.php`

## Observed implementation shape

- `class ProcessCameroon`
- `def __init__`
- `def download_raw_file`
- `def process_outage`
- `def process_region_file`
- `def run`
- `def main`
- `class CameroonScraper`
- `def __init__`
- `async def fetch_region`
- `async def scrape_all`
- `async def scrape_region`
- `def main`

Note: the original static scan omitted the three `async def` methods above (its pattern apparently only matched plain `def`). These are the scraper's core logic — `fetch_region` does the actual per-region HTTP POST to the endpoint, `scrape_all` fans out `fetch_region` across all 12 regions concurrently (bounded by `concurrent_connections`, default 3) and then invokes `ProcessCameroon.run()`, and `scrape_region` is a single-region CLI entry point.

## Imports / dependencies observed

- `from datetime import datetime`
- `from post_process import ProcessCameroon`
- `from utils.upload import Uploader`
- `import asyncio`
- `import httpx`
- `import json`
- `import os`
- `import sys`

## Output behavior

Observed output-related lines from code inspection:

- `L4: import json`
- `L7: from utils.upload import Uploader`
- `L24: self.uploader = Uploader(self.bucket_name)`
- `L42: def download_raw_file(self, region):`
- `L43: file_name = f"power_outages.CM.{region}.raw.{self.today}.json"`
- `L44: s3_path = f"cameroon/{region}/raw/{self.year}/{self.month}/{file_name}"`
- `L46: local_folder = f"./cameroon/{region}/raw/{self.year}/{self.month}"`
- `L51: self.uploader.download_file(s3_path, local_file_path)`
- `L52: print(f"[{region.upper()}] - downloaded raw data from S3")`
- `L56: print(f"[{region.upper()}] - using local raw data (missing from S3)")`
- `L118: file_path = self.download_raw_file(region)`
- `L120: print(f"[{region.upper()}] - raw file not found: {e}")`
- `L123: print(f"[{region.upper()}] - error downloading: {e}")`
- `L128: raw_data = json.load(file)`
- `L129: except json.JSONDecodeError as e:`
- `L130: print(f"[{region.upper()}] - invalid JSON in raw file: {e}")`
- `L136: processed_outages = []`
- `L138: if isinstance(raw_data, dict) and "data" in raw_data:`
- `L139: outages = raw_data["data"]`
- `L140: elif isinstance(raw_data, list):`
- `L141: outages = raw_data`
- `L147: processed = self.process_outage(outage, region)`
- `L148: if processed:`
- `L149: processed_outages.append(processed)`
- `L151: print(f"[{region.upper()}] ✓ Processed {len(processed_outages)} outages")`

Use neutral wording such as `observed output shape`, `processed provider-specific output`, and `current output behavior` unless direct evidence proves a stronger claim.

## Known risks / review notes

- `L264: http2=True, timeout=30.0, verify=False, follow_redirects=True`

## TODO / incomplete markers

- No TODO/TBD/FIXME/pass markers found by static scan.

## Runtime status

- Unknown — evidence needed unless a runtime validation report exists for this scraper.

## Documentation status

- This note is a generated draft and needs human review before being committed.
- Verify endpoint behavior, runtime output, and any provider-specific assumptions before treating this as final documentation.
