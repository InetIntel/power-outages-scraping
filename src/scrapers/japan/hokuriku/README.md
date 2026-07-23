# Japan Hokuriku Scraper Notes

Status: Draft generated from current repo evidence and validation-reviewed before packaging.

## Interpretation notes

- Line references such as `L###` are offsets from a generated per-folder Python inspection, not original source-file line numbers.
- Code terms such as `s3_path`, `Bucket`, and `list_objects_v2` may come from the current shared-volume `Uploader` shim and should not automatically be interpreted as active MinIO/S3 infrastructure.

## Registry

- Scraper ID: `japan_hokuriku`
- Module: `japan.hokuriku`
- Schedule: `0 1 * * *`
- Tags: `[japan, asia]`

## Files

- Scraper folder: `src/scrapers/japan/hokuriku`
- Python files: `post_process.py`, `scrape.py`
- Dockerfile: generated at build time by `publish.sh` from the root templates (not committed)
- requirements.txt present: Yes
- requirements.txt empty: No

## Source / endpoint evidence

- `https://www.rikuden.co.jp/nw/teiden/f2/sevendays/{self.date_str}/otj600.html`

- URL note: the observed URL includes a parameterized template segment (`{self.date_str}`). Verify runtime-expanded URLs before treating this as provider endpoint documentation.

## Observed implementation shape

- `class RikudenHTMLProcessor`
- `def __init__`
- `def _latest_html`
- `def _parse_table`
- `def clean` (nested helper defined inside `_parse_table`, not a class method — not callable as `processor.clean(...)`)
- `def run`
- `class RikudenHTMLScraper`
- `def __init__`
- `def fetch_html`
- `def save_html`
- `def run`

## Imports / dependencies observed

- `from bs4 import BeautifulSoup`
- `from datetime import datetime`
- `from datetime import datetime, timedelta, timezone`
- `from pathlib import Path`
- `from utils.upload import Uploader`
- `import json`
- `import requests`
- `import sys`

## Output behavior

Observed output-related lines from code inspection:

- `L7: import json`
- `L9: from utils.upload import Uploader`
- `L12: class RikudenHTMLProcessor:`
- `L15: self.raw_dir = base / "data" / "raw"`
- `L16: self.out_dir = base / "data" / "processed"`
- `L19: def _latest_html(self):`
- `L20: files = sorted(self.raw_dir.glob("rikuden_*.html"))`
- `L22: raise RuntimeError("No rikuden_*.html files found in raw/")`
- `L25: def _parse_table(self, html_bytes):`
- `L26: soup = BeautifulSoup(html_bytes, "html.parser")`
- `L55: households_raw = clean(cols[5])`
- `L56: reason_raw = clean(cols[6])`
- `L61: if households_raw`
- `L63: else households_raw`
- `L65: reason = None if reason_raw in ("―", "-", "") else reason_raw`
- `L82: uploader = Uploader("japan")`
- `L87: prefix = f"japan/hokuriku/raw/{year}/{month}/"`
- `L88: listing = uploader.client.list_objects_v2(Bucket="japan", Prefix=prefix)`
- `L91: local_path = self.raw_dir / Path(key).name`
- `L92: uploader.download_file(key, str(local_path))`
- `L94: html_path = self._latest_html()`
- `L95: print(f"Parsing -> {html_path}")`
- `L97: html_bytes = html_path.read_bytes()`
- `L98: entries = self._parse_table(html_bytes)`
- `L109: / f"rikuden_processed_{datetime.now().strftime('%Y%m%dT%H%M%S')}.json"`

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
