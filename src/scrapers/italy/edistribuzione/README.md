# Italy Power Outage Data (e-distribuzione)

## Data Retrieved
  
fid0 - ?, seems to be null often/always

note - string, customer facing message about status of the outage

objectid1 - int, unique identifier for the outage event

causa_interruzione - (English: interruption cause), string, internal code representing cause of outage

num_cli_disalim - (English: number of customers without power), int, number of customers affected by outage

dataultimoaggiornamento - (English: last update date), string, timestamp when outage event was most recently updated

descrizione_territoriale - (English: territorial description), string, territory associated with the outage

data_prev_ripristino - (English: estimated restoration date/time), string, timestamp of estimated outage restoration time

provincia - (English: province), string, province where the outage is occurring

cod_cs - string, internal code?

regione - (English: region), string, region where the outage is located

cft - string, internal code?

comune - int, ?

data_interruzione - (English: interruption start date), string, timestamp of when the outage began

latitudine - float, latitude coordinate of the outage location

x - always null?

id_interruzione - (English: interruption id), int, another outage event id?

y - always null?

causa_disalimentazione - (English: disconnection cause), string, human readable description of outage cause (in italian)

fid2 - int, ?

longitudine - float, longitude coordinate of the outage location

objectid - always null, another outage event id, possibly legacy identifier


## Data Retrieval

This dataset comes from e-distribuzione, a power provider in italy, which provides live information on current 
power outages in Italy. Data is accessed via the public api that is used to provide data to the live outage map 
on their website.

🔗 https://www.e-distribuzione.it/interruzione-corrente-primo.html

The API endpoint used:

https://ineuportalgis.enel.com/server/rest/services/Hosted/ITA_power_cut_map_layer_View/FeatureServer/0/query

Parameters used:
params = {
            "f": "json",
            "where": f"objectid1 > {last_id}",
            "outFields": "*",
            "returnGeometry": "true",
            "orderByFields": "objectid1 ASC",
            "resultRecordCount": 2000,
        }

Authentication:

This dataset is publicly accessible and does not require an API key.
However, requests should be rate-limited (e.g., 0.5–1.5 seconds between calls) to avoid throttling.

API Response Structure:

Each API response contains a JSON payload with an array of outage records in the features field. Each individual
outage then also contains an attributes and a geometry field:

{
  "features": [
    {
        "attributes": {
            "fid0": null,
            "note": "",
            "objectid1": 39928511,
            "causa_interruzione": "LV",
            "num_cli_disalim": 238,
            "dataultimoaggiornamento": "03/12/2025 08:00",
            "descrizione_territoriale": "ASSEMINI",
            "data_prev_ripristino": "03/12/2025 15:00",
            "provincia": "Cagliari",
            "cod_cs": "D7102123574",
            "regione": "Sardegna",
            "cft": "D000AA0",
            "comune": 92003,
            "data_interruzione": "03/12/2025 08:00",
            "latitudine": 39.28735568,
            "x": null,
            "id_interruzione": 1011886783,
            "y": null,
            "causa_disalimentazione": "Lavoro Programmato",
            "fid2": 0,
            "longitudine": 9.01587807,
            "objectid": null
        },
        "geometry": {
            "x": 1003642.9552714042,
            "y": 4762916.792617008
        },
    },
    ...
  ]
}

Code Process

> Rewritten 2026-07-22: previously said "Refer to spain/naturgy scraper" for both files without describing the actual logic. This scraper's pipeline is more involved than a simple fetch-and-upload — it maintains outage lifecycle state (`in_progress` / `resolved`) across runs via a `current_outages.json` file in the shared bucket.

**scrape.py** (Airflow `scrape` task):
1. `get_data()` pages through the ArcGIS FeatureServer using `objectid1 > last_id` cursor pagination (2000 records/page) until a page comes back empty.
2. Downloads today's pre-existing raw JSON (if any) and merges it with the new fetch via `update_raw_data()`, tagging each record `outage_ended_today: true/false` based on whether it disappeared from the new fetch.
3. Downloads `current_outages.json` (the running set of not-yet-resolved outages) and updates it via `update_current_outages()`: new outage IDs get `ioda_status: "in_progress"` plus `ioda_detection_date`/`ioda_update_date` timestamps; outages still present get `num_cli_disalim` (affected customers) bumped to the max seen and their update timestamp refreshed; outages that dropped out of the new fetch get `ioda_status: "resolved"`.
4. Uploads both the updated raw file and the updated `current_outages.json`.

**post_process.py** (Airflow `post_process` task):
1. Downloads `current_outages.json` and splits it into `resolved` vs. still-`in_progress` via `get_resolved_outages()`.
2. Re-uploads `current_outages.json` containing only the still-`in_progress` records (resolved ones are removed from the running state).
3. For each resolved outage, computes duration from `ioda_detection_date`/`ioda_update_date`, and builds a processed record with `country`, `start_utc`, `end_utc`, `duration_(hours)`, `event_category`, `clients_affected` (`num_cli_disalim`), and `area_affected` (`provincia`).
4. Appends these to the day's existing processed-data file (if any) and re-uploads.

## Known risks / review notes

- **Bug: outages are always categorized "Unplanned".** `post_process.py`'s `process_data()` has: `if type(outage["attributes"]["causa_disalimentazione"]) == "Lavoro Programmato":`. This compares a Python `type` object to a string, which is always `False` — `event_category` is therefore always set to `"Unplanned"`, even for genuinely planned outages (`causa_disalimentazione == "Lavoro Programmato"`, i.e. "Scheduled Work" — see the sample record above). The `type(...)` call should be removed so the comparison is against the value itself.


## Other Notes

The dataset updates every 5 minutes. Corrected 2026-07-22: the scraper (`italy_edistribuzione`) is actually scheduled every 4 hours (`0 */4 * * *` in `airflow/config/scraper_registry.yaml`), not every 4 minutes — this README previously misstated the schedule.

Outage categories are meant to include Planned (maintenance) and Unplanned (faults), but see the "Known risks" bug above — this distinction is not currently working.