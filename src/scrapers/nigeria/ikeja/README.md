# Nigeria Ikeja Scraper Notes

Status: Draft generated from current repo evidence and validation-reviewed before packaging.

## Interpretation notes

- Line references such as `L###` are offsets from a generated per-folder Python inspection, not original source-file line numbers.
- Code terms such as `s3_path`, `Bucket`, and `list_objects_v2` may come from the current shared-volume `Uploader` shim and should not automatically be interpreted as active MinIO/S3 infrastructure.

## Registry

- Scraper ID: `nigeria_ikeja`
- Module: `nigeria.ikeja`
- Schedule: `0 7 * * *`
- Tags: `[nigeria, africa]`

## Files

- Scraper folder: `src/scrapers/nigeria/ikeja`
- Python files: `post_process.py`, `scrape.py`
- Dockerfile: generated at build time by `publish.sh` from the root templates (not committed)
- requirements.txt present: Yes
- requirements.txt empty: No

## Source / endpoint evidence

- `https://www.ikejaelectric.com/cnn/`

## Observed implementation shape

- `class Process_Ikeja`
- `def __init__`
- `def download_raw_file`
- `def get_data`
- `def check_folder`
- `def save_json`
- `def run`
- `class Ikeja`
- `def __init__`
- `def check_folder`
- `async def fetch`
- `async def scrape`

Note: the original static scan omitted the two `async def` methods above (same pattern-matching gap found in `cameroon`'s README) — `fetch` is where the actual HTTP GET and inline post-processing call happen, and `scrape` is the `__main__` entry point.

## Imports / dependencies observed

- `from bs4 import BeautifulSoup`
- `from datetime import datetime`
- `from post_process import Process_Ikeja`
- `from utils.upload import Uploader`
- `import asyncio`
- `import httpx`
- `import json`
- `import os`
- `import sys`

## Output behavior

Observed output-related lines from code inspection:

- `L4: import json`
- `L8: from utils.upload import Uploader`
- `L19: self.uploader = Uploader(self.bucket_name)`
- `L20: print("Initialized uploader.")`
- `L22: print(f"Error initializing uploader: {e}")`
- `L23: self.uploader = None`
- `L25: def download_raw_file(self, date=None):`
- `L34: file_name = f"power_outages.NG.ikeja.raw.{date}.html"`
- `L35: s3_path = f"nigeria/ikeja/raw/{self.year}/{self.month}/{file_name}"`
- `L38: local_folder = f"./nigeria/ikeja/raw/{self.year}/{self.month}"`
- `L42: if not self.uploader:`
- `L43: raise Exception("Uploader not initialized")`
- `L46: print(f"Downloading raw file from S3: {s3_path}")`
- `L47: self.uploader.download_file(s3_path, local_file_path)`
- `L48: print(f"Downloaded raw file to: {local_file_path}")`
- `L52: print(f"Error downloading raw file from S3: {e}")`
- `L57: html_content = file.read()`
- `L59: soup = BeautifulSoup(html_content, "lxml")`
- `L102: def save_json(self, data):`
- `L103: self.check_folder("processed")`
- `L104: file_name = f"power_outages.NG.ikeja.processed.{self.today}.json"`
- `L108: json.dump(data, file, indent=4)`
- `L109: print(f"Saved processed data to: {file_path}")`
- `L111: if self.uploader:`
- `L112: s3_path = f"nigeria/ikeja/processed/{self.year}/{self.month}/{file_name}"`

Use neutral wording such as `observed output shape`, `processed provider-specific output`, and `current output behavior` unless direct evidence proves a stronger claim.

## Known risks / review notes

- `L187: http2=True, timeout=30.0, verify=False` — TLS verification is disabled on retry after a `CERTIFICATE_VERIFY_FAILED` connect error (`scrape.py`'s `fetch()`).
- **Processing runs twice per Airflow execution.** `scrape.py`'s `fetch()` uploads the raw HTML, then directly instantiates `Process_Ikeja(...).run()` inline (lines 57-62) — i.e. the `scrape` task already performs the full scrape → parse → upload-processed pipeline. The separate `post_process` Airflow task then runs `post_process.py`'s own `__main__`, which re-downloads that same raw file, re-parses it, and re-uploads the (identical) processed JSON. This is idempotent, not incorrect, but unlike every other scraper in this repo, `post_process.py` here is not the only processing step — it duplicates work already done during `scrape`.

## TODO / incomplete markers

- No TODO/TBD/FIXME/pass markers found by static scan.

## Runtime status

- Unknown — evidence needed unless a runtime validation report exists for this scraper.

## Documentation status

- This note is a generated draft and needs human review before being committed.
- Verify endpoint behavior, runtime output, and any provider-specific assumptions before treating this as final documentation.
