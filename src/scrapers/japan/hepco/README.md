# Japan Hepco Scraper Notes

Status: Draft generated from current repo evidence and validation-reviewed before packaging.

## Interpretation notes

- Line references such as `L###` are offsets from a generated per-folder Python inspection, not original source-file line numbers.
- Code terms such as `s3_path`, `Bucket`, and `list_objects_v2` may come from the current shared-volume `Uploader` shim and should not automatically be interpreted as active MinIO/S3 infrastructure.

## Registry

- Scraper ID: `japan_hepco`
- Module: `japan.hepco`
- Schedule: `0 1 * * *`
- Tags: `[japan, asia]`

## Files

- Scraper folder: `src/scrapers/japan/hepco`
- Python files: `post_process.py`, `scrape.py`
- Dockerfile: generated at build time by `publish.sh` from the root templates (not committed)
- requirements.txt present: Yes
- requirements.txt empty: No

## Source / endpoint evidence

- `https://teiden-info.hepco.co.jp/past00000000.html`

## Observed implementation shape

- `class HEPCOProcessor`
- `def __init__`
- `def parse_raw_outages`
- `def process_records`
- `def run`
- `class HEPCO`
- `def __init__`
- `def _get_output_path`
- `def fetch_html`
- `def save_html`
- `def run`

## Imports / dependencies observed

- `from bs4 import BeautifulSoup`
- `from datetime import datetime`
- `from pathlib import Path`
- `from utils.upload import Uploader`
- `import json`
- `import re`
- `import requests`

## Output behavior

Observed output-related lines from code inspection:

- `L5: import json`
- `L10: from utils.upload import Uploader`
- `L28: self.raw_filename = (`
- `L29: f"power_outages.JP.{self.provider}.raw.{self.today_iso}.html"`
- `L31: self.processed_filename = (`
- `L32: f"power_outages.JP.{self.provider}.processed.{self.today_iso}.json"`
- `L36: self.raw_path = Path(self.base_path) / "raw" / self.raw_filename`
- `L37: self.output_path = Path(self.base_path) / "processed" / self.processed_filename`
- `L40: def parse_raw_outages(self, html: str):`
- `L41: """Extract raw outage entries using regex patterns."""`
- `L42: soup = BeautifulSoup(html, "html.parser")`
- `L61: raw_records = []`
- `L64: raw_records.append(`
- `L76: print(f"Extracted {len(raw_records)} raw outage records")`
- `L77: return raw_records`
- `L79: def process_records(self, raw_records):`
- `L80: """Convert raw records into standardized outage entries."""`
- `L81: processed = []`
- `L82: for r in raw_records:`
- `L94: processed.append(`
- `L108: return processed`
- `L111: """Main entry point: load HTML -> parse -> process -> save JSON."""`
- `L112: uploader = Uploader("japan")`
- `L114: # Download raw file from shared volume`
- `L115: s3_path = f"japan/hepco/raw/{self.year}/{self.month}/{self.raw_filename}"`

Use neutral wording such as `observed output shape`, `processed provider-specific output`, and `current output behavior` unless direct evidence proves a stronger claim.

## Known risks / review notes

- No obvious risk keywords found by static scan.

## TODO / incomplete markers

- Corrected 2026-07-22: the original static scan reported none, but `post_process.py` has `except FileNotFoundError:\n    pass  # fall back to local file if available` in `HEPCOProcessor.run()` — a deliberate no-op (falls through to the `if not self.raw_path.exists(): raise ...` check just below), not a stub, but a real `pass` the scan missed.

## Runtime status

- Unknown — evidence needed unless a runtime validation report exists for this scraper.

## Documentation status

- This note is a generated draft and needs human review before being committed.
- Verify endpoint behavior, runtime output, and any provider-specific assumptions before treating this as final documentation.
