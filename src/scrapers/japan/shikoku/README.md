# Japan Shikoku Scraper Notes

Status: Draft generated from current repo evidence and validation-reviewed before packaging.

## Interpretation notes

- Line references such as `L###` are offsets from a generated per-folder Python inspection, not original source-file line numbers.
- Code terms such as `s3_path`, `Bucket`, and `list_objects_v2` may come from the current shared-volume `Uploader` shim and should not automatically be interpreted as active MinIO/S3 infrastructure.

## Registry

- Scraper ID: `japan_shikoku`
- Module: `japan.shikoku`
- Schedule: `0 1 * * *`
- Tags: `[japan, asia]`

## Files

- Scraper folder: `src/scrapers/japan/shikoku`
- Python files: `post_process.py`, `scrape.py`
- Dockerfile: generated at build time by `publish.sh` from the root templates (not committed)
- requirements.txt present: Yes
- requirements.txt empty: No

## Source / endpoint evidence

- `https://www.okidenmail.jp/bosai/api/xml_map2.php?date_key={date_key}&_={ts}`
- `https://www.okidenmail.jp/bosai/xml/history_normal.xml`

- Endpoint note: the listed `okidenmail.jp` URLs are observed implementation evidence, not confirmed Shikoku Electric provider endpoints.

## Observed implementation shape

- `class ShikokuProcessor`
- `def __init__`
- `def _to_iso`
- `def _clean_text`
- `def _parse_html`
- `def run`
- `class ShikokuScraper`
- `def __init__`
- `def fetch_master_xml`
- `def parse_date_keys`
- `def fetch_detail_xml`
- `def run`

## Imports / dependencies observed

- `from bs4 import BeautifulSoup`
- `from datetime import datetime`
- `from datetime import datetime, timezone, timedelta`
- `from pathlib import Path`
- `from utils.upload import Uploader`
- `from xml.etree import ElementTree as ET`
- `import json`
- `import os`
- `import re`
- `import requests`

## Output behavior

Observed output-related lines from code inspection:

- `L5: import json`
- `L10: from utils.upload import Uploader`
- `L21: self.raw_dir = self.base_dir / "data" / "raw"`
- `L22: self.processed_dir = self.base_dir / "data" / "processed"`
- `L23: self.processed_dir.mkdir(parents=True, exist_ok=True)`
- `L43: def _parse_html(self, html_text: str) -> list:`
- `L44: soup = BeautifulSoup(html_text, "html.parser")`
- `L50: occurrence_raw = h3.find("em", string="発生日時").next_sibling.strip()`
- `L51: recovery_raw = h3.find("em", string="復旧日時").next_sibling.strip()`
- `L52: occurrence = self._to_iso(occurrence_raw)`
- `L53: recovery = self._to_iso(recovery_raw)`
- `L106: uploader = Uploader("japan")`
- `L111: prefix = f"japan/shikoku/raw/{year}/{month}/"`
- `L112: listing = uploader.client.list_objects_v2(Bucket="japan", Prefix=prefix)`
- `L115: local_path = self.raw_dir / Path(key).name`
- `L116: uploader.download_file(key, str(local_path))`
- `L120: for file in sorted(self.raw_dir.glob("*.html")):`
- `L122: html = file.read_text(encoding="utf-8", errors="ignore")`
- `L123: entries = self._parse_html(html)`
- `L148: output_file = self.processed_dir / f"shikoku_outages_{self.today_iso}.json"`
- `L150: json.dump(filtered_outages, f, ensure_ascii=False, indent=2)`
- `L154: # Upload processed file to shared volume`
- `L155: s3_processed = f"japan/shikoku/processed/{year}/{month}/{output_file.name}"`
- `L156: uploader.upload_file(str(output_file), s3_processed)`
- `L170: from xml.etree import ElementTree as ET`

Use neutral wording such as `observed output shape`, `processed provider-specific output`, and `current output behavior` unless direct evidence proves a stronger claim.

## Known risks / review notes

- No obvious risk keywords found by static scan.

- Review warning: the current scraper is labeled Shikoku / 四国電力, but the inspected implementation uses Okinawa/OKIDEN endpoint evidence, including `okidenmail.jp`, `[OKIDEN]` log labels, and `okiden_master` filenames. Treat this as a likely source/provider mismatch until deeper review confirms the intended implementation.
- Confirmed 2026-07-22: this is not just a labeling mismatch — the pipeline is mechanically broken. `scrape.py` writes only `.xml` files (`okiden_master_{ts}.xml`, `okiden_{date_key}.xml`), but `post_process.py`'s `run()` globs exclusively for `*.html` (`self.raw_dir.glob("*.html")`), and `_parse_html()` targets HTML markup (`div.teiden_cont.detail`, `h3`/`em` tags with genuine Shikoku-style field labels like `発生日時`/`復旧日時`) that has no relation to the XML `scrape.py` fetches (`<data><date_key>` elements). No file `scrape.py` produces can ever match `post_process.py`'s glob, so `run()` always finds zero raw files and exits with "No valid outages found" — this scraper currently produces no processed output regardless of the provider question. `_parse_html()` reads like a genuine, purpose-built Shikoku HTML parser; `scrape.py` reads like it was copied from `japan/okinawa`'s fetch logic instead of a real Shikoku-specific fetch.

## TODO / incomplete markers

- `L81: # Skip empty or placeholder entries`

## Runtime status

- Unknown — evidence needed unless a runtime validation report exists for this scraper.

## Documentation status

- This note is a generated draft and needs human review before being committed.
- Verify endpoint behavior, runtime output, and any provider-specific assumptions before treating this as final documentation.
