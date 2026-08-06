# Japan Tohoku Scraper Notes

Status: Draft generated from current repo evidence and validation-reviewed before packaging.

## Interpretation notes

- Line references such as `L###` are offsets from a generated per-folder Python inspection, not original source-file line numbers.
- Code terms such as `s3_path`, `Bucket`, and `list_objects_v2` may come from the current shared-volume `Uploader` shim and should not automatically be interpreted as active MinIO/S3 infrastructure.

## Registry

- Scraper ID: `japan_tohoku`
- Module: `japan.tohoku`
- Schedule: `0 1 * * *`
- Tags: `[japan, asia]`

## Files

- Scraper folder: `src/scrapers/japan/tohoku`
- Python files: `post_process.py`, `scrape.py`
- Dockerfile: generated at build time by `publish.sh` from the root templates (not committed)
- requirements.txt present: Yes
- requirements.txt empty: No

## Source / endpoint evidence

- `https://nw.tohoku-epco.co.jp/teideninfo/blackout/`

## Observed implementation shape

> Corrected 2026-07-22: this list previously repeated itself (an artifact of the generation scan running twice), and the second copy of each class was missing methods the first copy had — deduplicated below to the actual unique set.

- `class TohokuScraper` (scrape.py)
- `def __init__`
- `def fetch_json`
- `def run`
- `def upload`
- `def run_and_upload`
- `class TohokuProcessor` (post_process.py)
- `def __init__`
- `def _get_raw_file_path`
- `def _get_output_file_path`
- `def _parse_outages`
- `def run`
- `def find_latest_raw_file` (module-level function, post_process.py)
- `def main` (module-level function, post_process.py)

## Imports / dependencies observed

- `from datetime import datetime`
- `from pathlib import Path`
- `from urllib.request import urlopen, Request`
- `from utils import Uploader`
- `from utils.upload import Uploader`
- `import json`
- `import ssl`

Corrected 2026-07-22: removed `import requests` — `scrape.py` line 4 is `# import requests`, commented out and unused; the actual HTTP fetch goes through `urlopen`/`Request` from `urllib.request` instead.

## Output behavior

Observed output-related lines from code inspection:

- `L4: import json`
- `L7: from utils.upload import Uploader`
- `L12: Processor for Tohoku Electric Power Company (東北電力) outage JSON data.`
- `L13: Reads a raw JSON file and outputs a processed summary file:`
- `L14: power_outages.JP.tohoku.processed.YYYY-MM-DD.json`
- `L26: def _get_raw_file_path(self):`
- `L27: """Path to the downloaded raw Tohoku JSON file."""`
- `L28: filename = f"power_outages.{self.country_code}.{self.provider}.raw.{self.today_iso}.json"`
- `L32: """Path to the processed output JSON file."""`
- `L33: filename = f"power_outages.{self.country_code}.{self.provider}.processed.{self.today_iso}.json"`
- `L36: def _parse_outages(self, raw_data):`
- `L37: """Extract outages from JSON into a consistent structured list."""`
- `L39: entries = raw_data.get("entries", [])`
- `L41: print("No entries found in Tohoku JSON data.")`
- `L95: """Parse and save processed JSON."""`
- `L97: raw_data = json.load(f)`
- `L99: outages = self._parse_outages(raw_data)`
- `L103: json.dump(outages, f, ensure_ascii=False, indent=2)`
- `L105: print(f"\nProcessed {len(outages)} outages -> {output_path.name}")`
- `L109: def find_latest_raw_file(uploader, bucket, prefix):`
- `L110: """Return the key of the most recent raw JSON file in the bucket.`
- `L115: response = uploader.client.list_objects_v2(Bucket=bucket, Prefix=prefix)`
- `L118: print("No files found in the raw folder.")`
- `L122: print(f"Latest raw file found: {latest}")`
- `L128: prefix = "japan/tohoku/raw/"`

Use neutral wording such as `observed output shape`, `processed provider-specific output`, and `current output behavior` unless direct evidence proves a stronger claim.

## Known risks / review notes

- `L189: # Use persistent /dagu/data path (shared with Dagu + MinIO)`
- `L190: self.base_path = Path("/dagu/data") / self.country / self.provider / "raw"`
- `L195: # Initialize uploader (use your MinIO bucket, e.g. "japan")`
- `L251: """Upload scraped file to MinIO/S3 via Uploader."""`
- `L252: s3_key = str(file_path).replace("/dagu/data/", "")  # Clean relative path`

- Review warning: active code contains stale DAGU-era path references such as `/dagu/data`. Review these paths against the current Airflow/Docker runtime path before treating the scraper documentation as final.

## TODO / incomplete markers

- `post_process.py` line 64: `except Exception: pass` (silently ignores a failed `start_dt` parse in `_parse_outages`)
- `post_process.py` line 72: `except Exception: pass` (silently ignores a failed `end_dt` parse in `_parse_outages`)
- Corrected 2026-07-22: the original list had four entries (`L67`, `L75`, `L422`, `L430`); the file is only 164 lines, so `L422`/`L430` couldn't be real — same duplication artifact as the "Observed implementation shape" section above. There are exactly two `pass` statements in this file.

## Runtime status

- Unknown — evidence needed unless a runtime validation report exists for this scraper.

## Documentation status

- This note is a generated draft and needs human review before being committed.
- Verify endpoint behavior, runtime output, and any provider-specific assumptions before treating this as final documentation.
