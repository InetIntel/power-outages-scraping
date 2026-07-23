# Brazil Aneel2 Scraper Notes

Status: Draft generated from current repo evidence and validation-reviewed before packaging.

## Interpretation notes

- Line references such as `L###` are offsets from a generated per-folder Python inspection, not original source-file line numbers.
- Code terms such as `s3_path`, `Bucket`, and `list_objects_v2` may come from the current shared-volume `Uploader` shim and should not automatically be interpreted as active MinIO/S3 infrastructure.

## Registry

- Scraper ID: `brazil_aneel2`
- Module: `brazil.aneel2`
- Schedule: none — runs after `brazil_aneel` completes (`depends_on: [brazil_aneel]`)
- Depends on: `[brazil_aneel]`
- Tags: `[brazil, south_america]`

## Files

- Scraper folder: `src/scrapers/brazil/aneel2`
- Python files: `Aneel.py`, `post_process.py`, `process.py`, `scrape.py`, `upload.py`
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
- `def process`
- `def upload`
- `def check_upload`

## Imports / dependencies observed

- `from Aneel import Aneel`
- `from bs4 import BeautifulSoup`
- `from datetime import datetime`
- `from tqdm import tqdm`
- `from utils import Uploader`
- `import os`
- `import requests`

## Output behavior

Observed output-related lines from code inspection:

- `L9: from utils import Uploader`
- `L15: self.uploader = Uploader("brazil")`
- `L21: f"./aneel/raw/{self.year}"  # the dir to store all scraped files/data in`
- `L28: _, _, tail = url.partition("/download/")`
- `L31: def __get_a_tags_from_html_page(self, html_page):`
- `L33: soup = BeautifulSoup(html_page, "html.parser")`
- `L38: if ".csv" in url and str(self.year) in filename:`
- `L43: def __download_csv(self, filename_and_url):`
- `L45: print("downloading csv")`
- `L54: def __download_csv_with_progress_bar(self, filename_and_url):`
- `L65: desc=f"Downloading {self.year}",`
- `L75: print(f"Downloading {self.year} data", flush=True)`
- `L80: filename_and_url = self.__get_a_tags_from_html_page(res.text)`
- `L88: print("starting download", flush=True)`
- `L90: self.__download_csv_with_progress_bar(filename_and_url)`
- `L92: self.__download_csv(filename_and_url)`
- `L94: print(f"Download for {self.year} data is complete")`
- `L102: def upload(self):`
- `L108: self.uploader.upload_file(local_path, s3_path)`
- `L110: print("Folder uploaded")`
- `L138: # FILE: upload.py`
- `L142: def check_upload(aneel):`
- `L143: response = aneel.uploader.client.list_objects_v2(Bucket="brazil")`
- `L154: s.upload()`
- `L155: check_upload(s)`

Use neutral wording such as `observed output shape`, `processed provider-specific output`, and `current output behavior` unless direct evidence proves a stronger claim.

## Known risks / review notes

- **Likely non-functional pipeline.** The Airflow DAG only ever runs `python scrape.py` then `python post_process.py` per scraper (see `airflow/dags/dag_factory.py`). Here, `scrape.py` calls `Aneel.scrape()`, which downloads CSVs to a local directory inside the container but never uploads them. `post_process.py` calls `Aneel.process()`, which is an empty `pass` stub. The only method that actually uploads data (`Aneel.upload()`) lives in `upload.py`, which is not wired into the DAG at all and is never invoked in production. Because task containers are auto-removed after each run, the downloaded CSVs are discarded when the `scrape` task container exits — this scraper currently persists no data.
- `process.py` and `post_process.py` are byte-identical (both just call `Aneel.process()`); one is likely a leftover duplicate.
- Contrast with `brazil/aneel` (no `2`), where `scrape.py`'s own `__main__` block calls both `scrape()` and `upload()` in one process — that variant does not have this problem.

## TODO / incomplete markers

- `L100: pass` — this is the empty `Aneel.process()` method invoked by the `post_process` Airflow task (see risk note above).

## Runtime status

- Unknown — evidence needed unless a runtime validation report exists for this scraper.

## Documentation status

- This note is a generated draft and needs human review before being committed.
- Verify endpoint behavior, runtime output, and any provider-specific assumptions before treating this as final documentation.
