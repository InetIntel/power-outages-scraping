# Japan Power Outage Scrapers

Scrapers for collecting and processing power outage data from the major Japanese power companies. In production these run as Docker containers orchestrated by Airflow — see the repo root `README.md` for the full deploy/run workflow. This document covers what is specific to the Japan scrapers.

## Layout

Each `<company>/` directory contains the standard scraper files:

1. **scrape.py** - Fetches raw data from the company's past-outages tables, either via endpoints serving XML, CSV, or JSON files, or by saving the page HTML when no data endpoint is available. Raw files are written under the scraper's `data/raw` directory.

2. **post_process.py** - Reads the raw files and converts them into a standardized JSON structure, written under `data/processed`.

3. **README.md** - Per-provider documentation (endpoints, data shape, known risks). These are generated drafts under review — verify against the code before trusting details.

## Running locally

From `src/scrapers/japan` with dependencies from the scraper's `requirements.txt` installed:

    python <company_name>/scrape.py
    python <company_name>/post_process.py

Run `scrape.py` first and confirm `data/raw` is populated before running `post_process.py`. In production the same two steps run as the `scrape` → `post_process` Airflow tasks.

## Output format

The exact fields vary slightly by source table, but in general:

- **Start**: The start time of the outage.
- **End**: The end time of the outage.
- **Area**: Where the outage occurred. The prefecture should always be included, sometimes along with cities and towns.
- **Households Affected**: Number of households affected; may be blank if under investigation or unknown.
- **Reason**: Cause of the outage; may also be blank if under investigation.

## Provider-specific notes

- It is often best to delete `data/raw` contents before rerunning `post_process.py`, as it may otherwise process duplicate instances of the same outage.
- Corrected 2026-07-22: all scrapers target roughly the past week of data. `tepco/scrape.py` and `tepco/post_process.py` both default to `days_back=7` ("last 7 days + today (8 total)" per the code's own docstring), and `tohoku/scrape.py`'s `run()` fetches `rirekiinfo01–07.json` and is documented in its own code comment as producing a "combined weekly JSON" — this README previously and incorrectly claimed TEPCO covers ~two months and Tohoku ~one month.
- **kyushu** scrapes a group of CSV files (40-46) that appear to align with ISO codes for Japan; the number of resultant files varies depending on which areas had outages.
- **tepco** returns `403 Forbidden` from some environments even though the endpoint is reachable from a browser — treat failures as request/access sensitivity, not a dead URL.
- **shikoku** currently points at Okinawa/OKIDEN endpoints (source/provider mismatch) — see its `README.md` before relying on its output.
- **tohoku** still writes to a stale DAGU-era `/dagu/data` path in `scrape.py` — pending fix.
