# Japan Chugoku Scraper Notes

Status: Draft generated from current repo evidence and validation-reviewed before packaging.

## Interpretation notes

- Line references such as `L###` are offsets from a generated per-folder Python inspection, not original source-file line numbers.
- Code terms such as `s3_path`, `Bucket`, and `list_objects_v2` may come from the current shared-volume `Uploader` shim and should not automatically be interpreted as active MinIO/S3 infrastructure.

## Registry

- Scraper ID: `japan_chugoku`
- Module: `japan.chugoku`
- Schedule: `0 1 * * *`
- Tags: `[japan, asia]`

## Files

- Scraper folder: `src/scrapers/japan/chugoku`
- Python files: `post_process.py`, `scrape.py`
- Dockerfile: generated at build time by `publish.sh` from the root templates (not committed)
- requirements.txt present: Yes
- requirements.txt empty: No

## Source / endpoint evidence

- `https://www.teideninfo.energia.co.jp/LWC30040/index`

## Observed implementation shape

- `def parse_event_block`
- `def parse_html_file`
- `def run`
- `class ChugokuHistoryScraper`
- `def __init__`
- `def fetch_html`
- `def save_html`
- `def run_single_day`
- `def run_last_n_days`

## Imports / dependencies observed

- `from bs4 import BeautifulSoup`
- `from datetime import datetime`
- `from datetime import datetime, timedelta, timezone`
- `from pathlib import Path`
- `from utils.upload import Uploader`
- `import json`
- `import os`
- `import requests`

## Output behavior

Observed output-related lines from code inspection:

- `L5: import json`
- `L9: from utils.upload import Uploader`
- `L13: RAW_DIR = BASE_DIR / "data" / "raw"`
- `L14: PROCESSED_DIR = BASE_DIR / "data" / "processed"`
- `L15: PROCESSED_DIR.mkdir(parents=True, exist_ok=True)`
- `L16: OUTPUT_FILE = PROCESSED_DIR / "combined_chugoku_processed.json"`
- `L74: def parse_html_file(filepath):`
- `L75: """Parse one HTML file for multiple event blocks."""`
- `L77: html = f.read()`
- `L79: soup = BeautifulSoup(html, "html.parser")`
- `L91: uploader = Uploader("japan")`
- `L96: prefix = f"japan/chugoku/raw/{year}/{month}/"`
- `L97: listing = uploader.client.list_objects_v2(Bucket="japan", Prefix=prefix)`
- `L100: local_path = RAW_DIR / Path(key).name`
- `L101: uploader.download_file(key, str(local_path))`
- `L105: for file in sorted(RAW_DIR.glob("*.html")):`
- `L107: events = parse_html_file(file)`
- `L112: json.dump(all_events, f, ensure_ascii=False, indent=2)`
- `L117: # Upload processed file to shared volume`
- `L118: s3_processed = f"japan/chugoku/processed/{year}/{month}/{OUTPUT_FILE.name}"`
- `L119: uploader.upload_file(str(OUTPUT_FILE), s3_processed)`
- `L131: from utils.upload import Uploader`
- `L135: """Scraper for Chugoku Electric Power — save raw HTML only."""`
- `L140: # Save to: <this_dir>/data/raw/`
- `L141: self.base_path = Path(__file__).resolve().parent / "data" / "raw"`

Use neutral wording such as `observed output shape`, `processed provider-specific output`, and `current output behavior` unless direct evidence proves a stronger claim.

## Known risks / review notes

- No obvious risk keywords found by static scan.

## TODO / incomplete markers

- No TODO/TBD/FIXME/pass markers found by static scan.

## Runtime status

- Unknown — evidence needed unless a runtime validation report exists for this scraper.

## Documentation status

- This note is a generated draft and needs human review before being committed.
- Verify endpoint behavior, runtime output, and any provider-specific assumptions before treating this as final documentation.
