# India Tangedco Scraper Notes

Status: Draft generated from current repo evidence and validation-reviewed before packaging.

## Interpretation notes

- Line references such as `L###` are offsets from a generated per-folder Python inspection, not original source-file line numbers.
- Code terms such as `s3_path`, `Bucket`, and `list_objects_v2` may come from the current shared-volume `Uploader` shim and should not automatically be interpreted as active MinIO/S3 infrastructure.

## Registry

- Scraper ID: `india_tangedco`
- Module: `india.tangedco`
- Schedule: `0 5 * * *`
- Tags: `[india, asia]`

## Files

- Scraper folder: `src/scrapers/india/tangedco`
- Python files: `post_process.py`, `scrape.py`
- Dockerfile: generated at build time by `publish.sh` from the root templates (not committed)
- requirements.txt present: Yes
- requirements.txt empty: No

## Source / endpoint evidence

- `https://tneb.tnebnet.org/cpro/today.html`

## Observed implementation shape

- `class ProcessTangedco`
- `def __init__`
- `def read_file`
- `def save`
- `def run`
- `def detect_and_run`
- `class TangedcoScraper`
- `def __init__`
- `def scrape`

## Imports / dependencies observed

- `from bs4 import BeautifulSoup`
- `from datetime import datetime`
- `import glob`
- `import json`
- `import os`
- `import requests`
- `import urllib3`

## Output behavior

Observed output-related lines from code inspection:

- `L5: import json`
- `L17: self.output_path = f"/data/india/tangedco/processed/{year}/{month}"`
- `L23: html = f.read()`
- `L25: print(f"Failed to read HTML: {e}")`
- `L28: soup = BeautifulSoup(html, "html.parser")`
- `L51: filename = f"power_outages.IND.tangedco.processed.{self.date}.json"`
- `L54: json.dump(data, f, indent=2, ensure_ascii=False)`
- `L64: "/data/india/tangedco/raw/*/*/power_outages.IND.tangedco.raw.*.html"`
- `L69: print(f"No raw files found under: {search_pattern}")`
- `L103: self.url = "https://tneb.tnebnet.org/cpro/today.html"`
- `L107: self.folder_path = f"/data/india/tangedco/raw/{self.year}/{self.month}"`
- `L117: filename = f"power_outages.IND.tangedco.raw.{self.today}.html"`

Use neutral wording such as `observed output shape`, `processed provider-specific output`, and `current output behavior` unless direct evidence proves a stronger claim.

- Note: unlike most scrapers in this repo, this one does not use the shared `utils.upload.Uploader`. It reads/writes directly to the hardcoded `/data/india/tangedco/...` paths on the mounted Docker volume via plain `os`/`open()` calls. `post_process.py`'s `detect_and_run()` also discovers its own input by globbing that raw path rather than being told a specific date/file.

## Known risks / review notes

- `L114: response = requests.get(self.url, verify=False, timeout=10)`

## TODO / incomplete markers

- No TODO/TBD/FIXME/pass markers found by static scan.

## Runtime status

- Unknown — evidence needed unless a runtime validation report exists for this scraper.

## Documentation status

- This note is a generated draft and needs human review before being committed.
- Verify endpoint behavior, runtime output, and any provider-specific assumptions before treating this as final documentation.
