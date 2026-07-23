# Japan Okinawa Scraper Notes

Status: Draft generated from current repo evidence and validation-reviewed before packaging.

## Interpretation notes

- Line references such as `L###` are offsets from a generated per-folder Python inspection, not original source-file line numbers.
- Code terms such as `s3_path`, `Bucket`, and `list_objects_v2` may come from the current shared-volume `Uploader` shim and should not automatically be interpreted as active MinIO/S3 infrastructure.

## Registry

- Scraper ID: `japan_okinawa`
- Module: `japan.okinawa`
- Schedule: `0 1 * * *`
- Tags: `[japan, asia]`

## Files

- Scraper folder: `src/scrapers/japan/okinawa`
- Python files: `post_process.py`, `scrape.py`
- Dockerfile: generated at build time by `publish.sh` from the root templates (not committed)
- requirements.txt present: Yes
- requirements.txt empty: No

## Source / endpoint evidence

- `https://www.okidenmail.jp/bosai/api/xml_map2.php`
- `https://www.okidenmail.jp/bosai/info2/`
- `https://www.okidenmail.jp/bosai/xml/history_normal.xml`

## Observed implementation shape

- `class OkinawaProcessor`
- `def __init__`
- `def parse_xml_file`
- `def run`
- `class OkidenScraper`
- `def __init__`
- `def fetch_master`
- `def parse_master_for_keys`
- `def fetch_detail`
- `def run`

## Imports / dependencies observed

- `from datetime import datetime`
- `from pathlib import Path`
- `from utils.upload import Uploader`
- `import json`
- `import requests`
- `import time`
- `import xml.etree.ElementTree as ET`

## Output behavior

Observed output-related lines from code inspection:

- `L4: import json`
- `L6: import xml.etree.ElementTree as ET`
- `L8: from utils.upload import Uploader`
- `L12: """Post-process Okinawa XML files into structured JSON."""`
- `L15: self.base_path = Path(__file__).resolve().parent / "data" / "raw"`
- `L16: self.output_path = self.base_path.parent / "processed"`
- `L18: self.output_file = self.output_path / "okinawa_processed.json"`
- `L20: def parse_xml_file(self, xml_path):`
- `L21: """Parse a single Okinawa XML file."""`
- `L23: tree = ET.parse(xml_path)`
- `L26: print(f"[WARN] Failed to parse {xml_path}: {e}")`
- `L85: print(f"[WARN] Failed to parse town entry in {xml_path}: {e}")`
- `L90: uploader = Uploader("japan")`
- `L95: prefix = f"japan/okinawa/raw/{year}/{month}/"`
- `L96: listing = uploader.client.list_objects_v2(Bucket="japan", Prefix=prefix)`
- `L100: uploader.download_file(key, str(local_path))`
- `L103: for xml_file in sorted(self.base_path.glob("*.xml")):`
- `L104: print(f"[PROCESS] Parsing {xml_file.name}")`
- `L105: outages = self.parse_xml_file(xml_file)`
- `L112: # Save combined JSON`
- `L114: json.dump(all_outages, f, ensure_ascii=False, indent=2)`
- `L118: # Upload processed file to shared volume`
- `L119: s3_processed = f"japan/okinawa/processed/{year}/{month}/{self.output_file.name}"`
- `L120: uploader.upload_file(str(self.output_file), s3_processed)`
- `L134: import xml.etree.ElementTree as ET`

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
