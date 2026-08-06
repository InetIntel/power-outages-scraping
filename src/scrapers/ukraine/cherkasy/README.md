# Ukraine Cherkasy Scraper Notes

Status: Draft generated from current repo evidence and validation-reviewed before packaging.

## Interpretation notes

- Line references such as `L###` are offsets from a generated per-folder Python inspection, not original source-file line numbers.
- Code terms such as `s3_path`, `Bucket`, and `list_objects_v2` may come from the current shared-volume `Uploader` shim and should not automatically be interpreted as active MinIO/S3 infrastructure.

## Registry

- Scraper ID: `ukraine_cherkasy`
- Module: `ukraine.cherkasy`
- Schedule: `0 */6 * * *`
- Tags: `[ukraine, europe]`

## Files

- Scraper folder: `src/scrapers/ukraine/cherkasy`
- Python files: `post_process.py`, `scrape.py`
- Dockerfile: generated at build time by `publish.sh` from the root templates (not committed)
- requirements.txt present: Yes
- requirements.txt empty: No

## Source / endpoint evidence

- `https://cabinet.cherkasyoblenergo.com/api_new/disconn.php`

## Observed implementation shape

- `class Process_Cherkasy`
- `def __init__`
- `def download_raw_file`
- `def get_data`
- `def check_folder`
- `def save_json`
- `def run`
- `class Cherkasy`
- `def __init__`
- `def check_folder`
- `async def fetch_single`
- `async def fetch_all`
- `async def scrape`

Note: the original static scan omitted the three `async def` methods above (same pattern-matching gap found in `cameroon`, `nigeria/ikeja`, and `thailand/mea`) — `fetch_all` fans out `fetch_single` across all disconnection types × department IDs concurrently and is where the inline post-processing call happens (see risk note below); `scrape` is the `__main__` entry point.

## Imports / dependencies observed

- `from datetime import datetime`
- `from dateutil.relativedelta import relativedelta`
- `from post_process import Process_Cherkasy`
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
- `L8: from utils.upload import Uploader`
- `L19: self.uploader = Uploader(self.bucket_name)`
- `L21: print(f"error initializing uploader: {e}")`
- `L22: self.uploader = None`
- `L24: def download_raw_file(self, date=None):`
- `L33: file_name = f"power_outages.UA.cherkasy.raw.{date}.json"`
- `L34: s3_path = f"ukraine/cherkasy/raw/{self.year}/{self.month}/{file_name}"`
- `L37: local_folder = f"./ukraine/cherkasy/raw/{self.year}/{self.month}"`
- `L41: if not self.uploader:`
- `L42: raise Exception("uploader not initialized")`
- `L45: self.uploader.download_file(s3_path, local_file_path)`
- `L49: print(f"error downloading raw file from S3: {e}")`
- `L54: data = json.load(file)`
- `L74: end_raw = disconnection.get("DATE_STOP", "")`
- `L76: if not start or not end_raw:`
- `L80: end = end_raw.split("(")[0].strip()`
- `L90: areas_affected_raw = disconnection.get("ADDRESS", "")`
- `L93: matches = re.findall(r"<br>(.*?)<br>", areas_affected_raw)`
- `L128: def save_json(self, data):`
- `L129: self.check_folder("processed")`
- `L130: file_name = f"power_outages.UA.cherkasy.processed.{self.today}.json"`
- `L134: json.dump(data, file, ensure_ascii=False, indent=4)`
- `L135: print(f"saved processed data to: {file_path}")`
- `L137: if self.uploader:`

Use neutral wording such as `observed output shape`, `processed provider-specific output`, and `current output behavior` unless direct evidence proves a stronger claim.

## Known risks / review notes

- `L245: async with httpx.AsyncClient(http2=True, timeout=30.0, verify=False) as client:` — TLS verification is deliberately disabled here; the code comment directly above it explains why (`# disable SSL verification due to certificate issues with the API`), so this is a documented workaround, not an oversight.
- **Processing runs twice per Airflow execution**, same pattern as `nigeria/ikeja`. `scrape.py`'s `fetch_all()` uploads the raw data, then directly instantiates `Process_Cherkasy(...).run()` inline (lines 99-104) — i.e. the `scrape` task already performs the full scrape → parse → upload-processed pipeline. The separate `post_process` Airflow task then runs `post_process.py`'s own `__main__`, which re-downloads that same raw file, re-parses it, and re-uploads the (identical) processed JSON. Idempotent, not incorrect, but duplicated work.

## TODO / incomplete markers

- No TODO/TBD/FIXME/pass markers found by static scan.

## Runtime status

- Unknown — evidence needed unless a runtime validation report exists for this scraper.

## Documentation status

- This note is a generated draft and needs human review before being committed.
- Verify endpoint behavior, runtime output, and any provider-specific assumptions before treating this as final documentation.
