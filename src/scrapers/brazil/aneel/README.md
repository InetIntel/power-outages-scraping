# Brazil Aneel Scraper Notes

Status: Draft generated from current repo evidence and validation-reviewed before packaging.

## Interpretation notes

- Line references such as `L###` are offsets from a generated per-folder Python inspection, not original source-file line numbers.
- Code terms such as `s3_path`, `Bucket`, and `list_objects_v2` may come from the current shared-volume `Uploader` shim and should not automatically be interpreted as active MinIO/S3 infrastructure.

## Registry

- Scraper ID: `brazil_aneel`
- Module: `brazil.aneel`
- Schedule: `0 */4 * * *`
- Tags: `[brazil, south_america]`

## Files

- Scraper folder: `src/scrapers/brazil/aneel`
- Python files: `post_process.py`, `scrape.py`
- Dockerfile: generated at build time by `publish.sh` from the root templates (not committed)
- requirements.txt present: Yes
- requirements.txt empty: No

## Source / endpoint evidence

- `https://dadosabertos.aneel.gov.br/dataset/interrupcoes-de-energia-eletrica-nas-redes-de-distribuicao`

## Observed implementation shape

- `class Aneel`
- `def __init__`
- `def __create_dir`
- `def __get_filename_from_url`
- `def __get_a_tags_from_html_page`
- `def __download_csv`
- `def __download_csv_with_progress_bar`
- `def scrape`
- `def upload`

## Imports / dependencies observed

- `from bs4 import BeautifulSoup`
- `from datetime import datetime`
- `from tqdm import tqdm`
- `from utils import Uploader`
- `from utils.upload import Uploader`
- `import os`
- `import requests`

## Output behavior

Observed output-related lines from code inspection:

- `L4: from utils.upload import Uploader`
- `L7: uploader = Uploader("brazil")`
- `L8: response = uploader.client.list_objects_v2(Bucket="brazil")`
- `L24: from utils import Uploader`
- `L28: def __init__(self, uploader, year=None):`
- `L30: self.uploader = uploader`
- `L36: f"./aneel/raw/{self.year}"  # the dir to store all scraped files/data in`
- `L43: _, _, tail = url.partition("/download/")`
- `L46: def __get_a_tags_from_html_page(self, html_page):`
- `L48: soup = BeautifulSoup(html_page, "html.parser")`
- `L53: if ".csv" in url and str(self.year) in filename:`
- `L58: def __download_csv(self, filename_and_url):`
- `L60: print("downloading csv")`
- `L69: def __download_csv_with_progress_bar(self, filename_and_url):`
- `L80: desc=f"Downloading {self.year}",`
- `L90: print(f"Downloading {self.year} data", flush=True)`
- `L95: filename_and_url = self.__get_a_tags_from_html_page(res.text)`
- `L103: print("starting download", flush=True)`
- `L105: self.__download_csv_with_progress_bar(filename_and_url)`
- `L107: self.__download_csv(filename_and_url)`
- `L109: print(f"Download for {self.year} data is complete")`
- `L111: def upload(self):`
- `L117: self.uploader.upload_file(local_path, s3_path)`
- `L119: print("✅ Folder uploaded")`
- `L125: s = Aneel(Uploader("brazil"))`

Use neutral wording such as `observed output shape`, `processed provider-specific output`, and `current output behavior` unless direct evidence proves a stronger claim.

- Note: unlike most scrapers in this repo, there is no structured output stage. `scrape.py` downloads ANEEL's raw CSV files as-is (no field parsing) and uploads the whole folder. `post_process.py` does not transform anything — it only lists the bucket's existing contents via `list_objects_v2` as a diagnostic check.

## Known risks / review notes

- No obvious risk keywords found by static scan.

## TODO / incomplete markers

- No TODO/TBD/FIXME/pass markers found by static scan.

## Runtime status

- Unknown — evidence needed unless a runtime validation report exists for this scraper.

## Documentation status

- This note is a generated draft and needs human review before being committed.
- Verify endpoint behavior, runtime output, and any provider-specific assumptions before treating this as final documentation.
