# Japan Tepco Scraper Notes

Status: Draft generated from current repo evidence and validation-reviewed before packaging.

## Interpretation notes

- Line references such as `L###` are offsets from a generated per-folder Python inspection, not original source-file line numbers.
- Code terms such as `s3_path`, `Bucket`, and `list_objects_v2` may come from the current shared-volume `Uploader` shim and should not automatically be interpreted as active MinIO/S3 infrastructure.

## Registry

- Scraper ID: `japan_tepco`
- Module: `japan.tepco`
- Schedule: `0 1 * * *`
- Tags: `[japan, asia]`

## Files

- Scraper folder: `src/scrapers/japan/tepco`
- Python files: `post_process.py`, `scrape.py`
- Dockerfile: generated at build time by `publish.sh` from the root templates (not committed)
- requirements.txt present: Yes
- requirements.txt empty: No

## Source / endpoint evidence

- `https://teideninfo.tepco.co.jp/day/teiden/`

## Observed implementation shape

- `class TEPCOProcessor`
- `def __init__`
- `def _get_raw_file_path`
- `def _get_output_path`
- `def _parse_outages`
- `def run`
- `class TEPCOScraper`
- `def __init__`
- `def _get_output_path`
- `def _get_remote_filename`
- `def fetch_and_save`
- `def run`

## Imports / dependencies observed

- `from bs4 import BeautifulSoup`
- `from datetime import datetime, timedelta`
- `from pathlib import Path`
- `from utils.upload import Uploader`
- `import json`
- `import requests`

## Output behavior

Observed output-related lines from code inspection:

- `L7: import json`
- `L8: from utils.upload import Uploader`
- `L13: Processor for Tokyo Electric Power Company (TEPCO) XML outage data.`
- `L14: Combines the last 7 days of XML files into a single JSON file:`
- `L15: power_outages.JP.tepco.processed.YYYY-MM-DD.json`
- `L25: (self.data_dir / "processed").mkdir(parents=True, exist_ok=True)`
- `L30: def _get_raw_file_path(self, date: datetime):`
- `L31: """Return path to the raw XML file for the given date."""`
- `L34: f"power_outages.{self.country_code}.{self.provider}.raw.{date_str}.xml"`
- `L36: return self.data_dir / "raw" / filename`
- `L39: """Single combined weekly JSON output file in data directory."""`
- `L40: filename = f"power_outages.{self.country_code}.{self.provider}.processed.{self.today_iso}.json"`
- `L41: return self.data_dir / "processed" / filename`
- `L43: def _parse_outages(self, xml_content: str):`
- `L44: """Parse one XML file into a list of outage dicts."""`
- `L45: soup = BeautifulSoup(xml_content, "xml")`
- `L84: """Parse and combine the last `days_back` days of XML into one JSON file."""`
- `L85: uploader = Uploader("japan")`
- `L87: # Download raw files from shared volume`
- `L90: raw_path = self._get_raw_file_path(date)`
- `L93: s3_path = f"japan/tepco/raw/{date_year}/{date_month}/{raw_path.name}"`
- `L95: raw_path.parent.mkdir(parents=True, exist_ok=True)`
- `L96: uploader.download_file(s3_path, str(raw_path))`
- `L104: raw_path = self._get_raw_file_path(date)`
- `L105: if not raw_path.exists():`

Use neutral wording such as `observed output shape`, `processed provider-specific output`, and `current output behavior` unless direct evidence proves a stronger claim.

## Known risks / review notes

- No obvious risk keywords found by static scan.

## TODO / incomplete markers

- Corrected 2026-07-22: the scan reported none, but `post_process.py`'s `run()` has `except FileNotFoundError:\n    pass  # fall back to local file if available` — the same deliberate-fallback pattern missed in `japan/hepco` and `japan/kansai`.

## Runtime status

- Unknown — evidence needed unless a runtime validation report exists for this scraper.

## Documentation status

- This note is a generated draft and needs human review before being committed.
- Verify endpoint behavior, runtime output, and any provider-specific assumptions before treating this as final documentation.
