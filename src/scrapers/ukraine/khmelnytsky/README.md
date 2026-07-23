# Ukraine Khmelnytsky Scraper Notes

Status: Draft generated from current repo evidence and validation-reviewed before packaging.

## Interpretation notes

- Line references such as `L###` are offsets from a generated per-folder Python inspection, not original source-file line numbers.
- Code terms such as `s3_path`, `Bucket`, and `list_objects_v2` may come from the current shared-volume `Uploader` shim and should not automatically be interpreted as active MinIO/S3 infrastructure.

## Registry

- Scraper ID: `ukraine_khmelnytsky`
- Module: `ukraine.khmelnytsky`
- Schedule: `0 */6 * * *`
- Tags: `[ukraine, europe]`

## Files

- Scraper folder: `src/scrapers/ukraine/khmelnytsky`
- Python files: `post_process.py`, `scrape.py`
- Dockerfile: generated at build time by `publish.sh` from the root templates (not committed)
- requirements.txt present: Yes
- requirements.txt empty: No

## Source / endpoint evidence

- `https://hoe.com.ua/shutdown/eventlist`

## Observed implementation shape

- `class Process_Khmelnytsky`
- `def __init__`
- `def download_raw_files`
- `def get_data`
- `def check_folder`
- `def save_json`
- `def run`
- `class Khmelnytsky`
- `def __init__`
- `def check_folder`
- `async def fetch_single`
- `async def fetch_all`
- `async def scrape`

Note: the original static scan omitted the three `async def` methods above (same pattern-matching gap found in `cameroon`, `nigeria/ikeja`, `thailand/mea`, and `ukraine/cherkasy`) — `fetch_all` fans out `fetch_single` across all 6 regions concurrently and is where the inline post-processing call happens (see risk note below); `scrape` is the `__main__` entry point.

## Imports / dependencies observed

- `from datetime import datetime`
- `from datetime import datetime, timedelta`
- `from post_process import Process_Khmelnytsky`
- `from utils.upload import Uploader`
- `import asyncio`
- `import glob`
- `import httpx`
- `import json`
- `import lxml.html`
- `import os`
- `import sys`

## Output behavior

Observed output-related lines from code inspection:

- `L4: import json`
- `L8: import lxml.html`
- `L9: from utils.upload import Uploader`
- `L21: self.uploader = Uploader(self.bucket_name)`
- `L23: print(f"error initializing uploader: {e}")`
- `L24: self.uploader = None`
- `L26: def download_raw_files(self, date=None):`
- `L36: local_folder = f"./ukraine/khmelnytsky/raw/{self.year}/{self.month}"`
- `L39: if not self.uploader:`
- `L40: raise Exception("Uploader not initialized")`
- `L42: downloaded_files = []`
- `L44: file_name = f"power_outages.UA.khmelnytsky.raw.{date}.{region}.html"`
- `L45: s3_path = f"ukraine/khmelnytsky/raw/{self.year}/{self.month}/{file_name}"`
- `L49: self.uploader.download_file(s3_path, local_file_path)`
- `L50: downloaded_files.append(local_file_path)`
- `L52: print(f"error downloading raw file for region {region} from S3: {e}")`
- `L56: return downloaded_files`
- `L59: # get all HTML files for today`
- `L60: raw_folder = f"./ukraine/khmelnytsky/raw/{self.year}/{self.month}"`
- `L61: file_pattern = f"power_outages.UA.khmelnytsky.raw.{self.today}.*.html"`
- `L62: files = glob.glob(os.path.join(raw_folder, file_pattern))`
- `L66: f"no HTML files found in {raw_folder} matching pattern {file_pattern}"`
- `L77: html_content = f.read()`
- `L78: html_page = lxml.html.fromstring(html_content)`
- `L81: planned_disconnections = html_page.xpath("//tbody/tr[not(@class)]")`

Use neutral wording such as `observed output shape`, `processed provider-specific output`, and `current output behavior` unless direct evidence proves a stronger claim.

## Known risks / review notes

- `L270: async with httpx.AsyncClient(http2=True, timeout=30.0, verify=False) as client:` — TLS verification is deliberately disabled; the code comment directly above it explains why (`# disable SSL verification due to potential certificate issues`), so this is a documented workaround, not an oversight.
- **Processing runs twice per Airflow execution**, same pattern as `ukraine/cherkasy` and `nigeria/ikeja`. `scrape.py`'s `fetch_all()` uploads each region's raw HTML, then directly instantiates `Process_Khmelnytsky(...).run()` inline (lines 107-112) — i.e. the `scrape` task already performs the full scrape → parse → upload-processed pipeline. The separate `post_process` Airflow task then runs `post_process.py`'s own `__main__`, which re-downloads the same raw files, re-parses them, and re-uploads the (identical) processed JSON. Idempotent, not incorrect, but duplicated work.

## TODO / incomplete markers

- `L176: pass`

## Runtime status

- Unknown — evidence needed unless a runtime validation report exists for this scraper.

## Documentation status

- This note is a generated draft and needs human review before being committed.
- Verify endpoint behavior, runtime output, and any provider-specific assumptions before treating this as final documentation.
