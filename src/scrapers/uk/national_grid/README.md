# UK Power Outage Data (National Grid)

Note on the Data Retrieved and the Process of Retrieval
## Data Retrieved ##

_id (corrected 2026-07-22, was listed as "id" — matches the sample response below) – internal index number for the dataset record, added by the source or API. This is not global. It is only for this data pull.
Example: 1

Upload Date – timestamp of when this outage record was last updated or uploaded to the National Grid API.
Example: 2025-10-20T22:20:00

Region – regional descriptor for the affected area served by the National Grid.
Example: South West

Incident ID – unique identifier for the specific outage event.
Example: INCD-72381-l

Confirmed Off – integer representing the number of customers confirmed to have lost supply.
Example: 49

Predicted Off – integer representing the number of customers predicted (but not confirmed) to be off supply.
Example: 0

Restored – integer representing the number of customers whose power has been restored.
Example: 16

Status – string description of the current state of the outage.
Example: In Progress

Planned – boolean indicating if the outage is planned maintenance (true) or an unplanned fault (false).
Example: false

Category – descriptor of the outage type or asset affected.
Example: LV UNDERGROUND

Resource Status – short status code from the National Grid indicating outage resolution state or field resource dispatch.
Example: ONS

Start Time – datetime of when the outage began.
Example: 2025-10-20T14:56:00

ETR (Estimated Time of Restoration) – datetime for the estimated time when power will be restored.
Example: 2025-10-21T01:00:00

Voltage – voltage level of the affected network segment (e.g. LV for Low Voltage, HV for High Voltage).
Example: LV

Location Latitude / Longitude – numeric coordinates representing the central point of the outage.
Example: 50.97075, -2.762076

Postcodes – comma-separated list of postal codes impacted by the outage.
Example: "TA12 6LZ, TA12 6PG, TA12 6PL, TA12 6NG"

## Data Retrieval ##

This dataset comes from the UK National Grid’s Open Data Portal, specifically the live outage dataset located here:
🔗 https://connecteddata.nationalgrid.co.uk/dataset/live-power-cuts/resource/292f788f-4339-455b-8cc0-153e14509d4d

This dataset provides current and recent power outage events for the National Grid’s electricity distribution network in the UK.

The API endpoint used is the CKAN DataStore API, which provides paginated JSON data access to datasets hosted on the National Grid portal.

url = "https://connecteddata.nationalgrid.co.uk/api/3/action/datastore_search"


Parameters used:

params = {
    "resource_id": "292f788f-4339-455b-8cc0-153e14509d4d",  # unique resource identifier for live outage data
    "limit": 1000,  # number of records to retrieve per call
    "offset": offset  # used to paginate through all available results
}


No authentication or API key is required to access this data.
Data is returned as a JSON object with the structure:

{
  "result": {
    "records": [
      {
        "_id": 1,
        "Upload Date": "2025-10-20T22:20:00",
        "Region": "South West",
        ...
      }
    ]
  }
}

Code Process

> Corrected 2026-07-22: this section previously described `crawler.py`'s pandas/CSV logic. That is not what runs in production — the Airflow DAG only ever executes `scrape.py` then `post_process.py` (see `airflow/dags/dag_factory.py`), and `crawler.py` is a legacy standalone script. Confirmed: `requirements.txt` lists only `requests`, so `crawler.py` (which imports `pandas`) could not run inside the built scraper image.

**`scrape.py`** (Airflow `scrape` task):
1. Pages through the CKAN DataStore API 1,000 records at a time (`offset`/`limit`) until a page returns fewer than `limit` records or an empty page.
2. Deduplicates in-memory by `Incident ID` using a Python `set` (not pandas), keeping the first record seen per ID (crawler.py's `drop_duplicates(..., keep="last")` behavior is not replicated here).
3. Writes the deduplicated records as `power_outages.GB.national_grid.raw.<date>.json` to a local temp path, uploads it via `Uploader` to `national_grid/raw/<year>/<month>/`, then deletes the local temp file.

**`post_process.py`** (Airflow `post_process` task):
1. Downloads that same-day raw JSON file.
2. Re-uploads it unchanged as `national_grid/processed/<year>/<month>/power_outages.GB.national_grid.processed.<date>.json` — no field parsing, filtering, or further deduplication happens here.
3. Accepts an optional `YYYY-MM-DD` argument to reprocess a past date.

**`crawler.py`** (legacy, not run by Airflow): an earlier standalone version that accumulates results into a pandas DataFrame and appends to a local CSV (`national_grid_power_outage.csv`), deduplicating on `Incident ID` with `keep="last"`. Kept for reference only.

## Other Notes ##

The dataset is live and frequently updated every 5 minutes by the National Grid.

We should be polling data either every 5 minutes (just after the data update) or faster. As of 2026-07-22, the actual configured schedule (`uk_national_grid` in `airflow/config/scraper_registry.yaml`) is every 2 hours (`0 */2 * * *`) — well short of this recommendation; noting the gap for future tuning rather than treating "every 5 minutes" as the current behavior.

All data is in GMT time