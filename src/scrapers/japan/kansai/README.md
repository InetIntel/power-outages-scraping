# Japan Kansai Scraper Notes

Status: Draft generated from current repo evidence and validation-reviewed before packaging.

## Interpretation notes

- Line references such as `L###` are offsets from a generated per-folder Python inspection, not original source-file line numbers.
- Code terms such as `s3_path`, `Bucket`, and `list_objects_v2` may come from the current shared-volume `Uploader` shim and should not automatically be interpreted as active MinIO/S3 infrastructure.

## Registry

- Scraper ID: `japan_kansai`
- Module: `japan.kansai`
- Schedule: `0 1 * * *`
- Tags: `[japan, asia]`

## Files

- Scraper folder: `src/scrapers/japan/kansai`
- Python files: `post_process.py`, `scrape.py`
- Dockerfile: generated at build time by `publish.sh` from the root templates (not committed)
- requirements.txt present: Yes
- requirements.txt empty: No

## Source / endpoint evidence

- `https://www.kansai-td.co.jp/interchange/teiden-info/ja/history.json`
- Note: `fetch_json()` appends a `?_=<JST-timestamp>` cache-busting query parameter at request time; it does not change which resource is fetched.

## Observed implementation shape

- `class KansaiProcessor`
- `def __init__`
- `def _get_raw_file_path`
- `def _get_output_file_path`
- `def _parse_outages`
- `def run`
- `class KansaiScraper`
- `def __init__`
- `def fetch_json`
- `def run`

## Imports / dependencies observed

- `from datetime import datetime, timedelta, timezone`
- `from pathlib import Path`
- `from urllib.request import urlopen, Request`
- `from utils.upload import Uploader`
- `import json`
- `import requests`
- `import ssl`

## Output behavior

Observed output-related lines from code inspection:

- `L6: import json`
- `L7: from utils.upload import Uploader`
- `L13: Reads a single raw JSON file and outputs a processed summary file:`
- `L14: power_outages.JP.kansai.processed.YYYY-MM-DD.json`
- `L24: (self.data_dir / "processed").mkdir(parents=True, exist_ok=True)`
- `L31: def _get_raw_file_path(self):`
- `L32: """Path to the raw Kansai JSON file."""`
- `L33: filename = f"power_outages.{self.country_code}.{self.provider}.raw.{self.today_iso}.json"`
- `L34: return self.data_dir / "raw" / filename`
- `L37: """Path to the processed output JSON file."""`
- `L38: filename = f"power_outages.{self.country_code}.{self.provider}.processed.{self.today_iso}.json"`
- `L39: return self.data_dir / "processed" / filename`
- `L41: def _parse_outages(self, raw_data):`
- `L42: """Parse Kansai JSON data into a flattened structured list."""`
- `L45: entries = raw_data.get("entries", {}).get("list", [])`
- `L104: """Run processor to parse and save processed JSON."""`
- `L105: uploader = Uploader("japan")`
- `L109: input_path = self._get_raw_file_path()`
- `L111: # Download raw file from shared volume`
- `L112: raw_filename = input_path.name`
- `L113: s3_path = f"japan/kansai/raw/{year}/{month}/{raw_filename}"`
- `L116: uploader.download_file(s3_path, str(input_path))`
- `L121: print(f"Raw Kansai JSON not found: {input_path}")`
- `L125: raw_data = json.load(f)`
- `L127: outages = self._parse_outages(raw_data)`

Use neutral wording such as `observed output shape`, `processed provider-specific output`, and `current output behavior` unless direct evidence proves a stronger claim.

## Known risks / review notes

- `L169: # self.base_path = Path("/dagu/data")`

## TODO / incomplete markers

- `L72: pass` (silently ignores a failed `start_dt` parse in `_parse_outages`)
- `L79: pass` (silently ignores a failed `end_dt` parse in `_parse_outages`)
- Corrected 2026-07-22: the scan also missed a third `pass` — `post_process.py`'s `run()` has `except FileNotFoundError:\n    pass  # fall back to local file if available`, the same deliberate-fallback pattern found missing from `japan/hepco`'s scan.

## Runtime status

- Unknown — evidence needed unless a runtime validation report exists for this scraper.

## Documentation status

- This note is a generated draft and needs human review before being committed.
- Verify endpoint behavior, runtime output, and any provider-specific assumptions before treating this as final documentation.
