# Spain Power Outage Data (e-distribución / Endesa)

## Data Retrieved

note - string, A brief message to the customer describing the status of the outage.

objectid1 - int, unique integer identifier for the outage event. helpful for tracking an individual outage across multiple 
scraper runs.

cod_cause - string, short code for the outage cause.

latitude - latitude coordinate of the outage location.

municipality - string, town or city where the outage is occuring.

reposition_date - string, expected date and time when the power will be restored. (Corrected 2026-07-22: field name has an underscore, not a space — matches `reposition_date` in the sample record below.)

service_des_ca - ?

affected_client - int, number of clients affected by the outage. (Corrected 2026-07-22: field name has an underscore, not a space — matches `affected_client` used in `post_process.py` and the sample record below.)

des_cause_es - ?

cft - string, internal code representing operational zone

des_cause_en - string, description of the outage cause in english.

service_type - string, internal code for category of service

update_time - string, timestamp of the most recent update to the outage record

interruption_date - string, timestamp of when the outage started

service_des_es - ?

des_cause_ca - ?

cd_code - internal code?

objectid - appears to be a second id, but is often null. maybe an old feature?

longitude - longitude coordinate of the location of the outage

service_des_en - string, description of the service issue in english

territory - ?



## Data Retrieval

This dataset comes from e-distribucion, a power provider in spain, which provides live information on current and 
planned power outages in Spain. Data is accessed via the public api that is used to provide data to the live outage map 
on their website.

🔗 https://www.edistribucion.com/en/averias.html

The API endpoint used:

https://ineuportalgis.enel.com/server/rest/services/Hosted/ESP_Prod_power_cut_View/FeatureServer/0/query

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
            "note": "Su suministro está afectado por una incidencia, estamos trabajando en su resolución.",
            "objectid1": 81232447,
            "cod_cause": "A",
            "latitude": 38.44913307,
            "municipality": "Zafra",
            "reposition_date": "03/12/2025 04:00",
            "service_des_ca": "Avaria BT",
            "affected_client": 1,
            "des_cause_es": "Avería",
            "cft": "Zafra",
            "des_cause_en": "Unplanned outage",
            "service_type": "GB",
            "update_time": "03/12/2025 03:45",
            "interruption_date": "02/12/2025 21:52",
            "service_des_es": "Avería BT",
            "des_cause_ca": "Avaria",
            "cd_code": "47210",
            "objectid": null,
            "longitude": -6.42684356,
            "service_des_en": "Unplanned Outage BT",
            "territory": "AND"
        },
        "geometry": {
            "x": -715432.9520059079,
            "y": 4643068.992276251
        },
    },
    ...
  ]
}

Code Process

> Rewritten 2026-07-22: previously said "Refer to spain/naturgy scraper" for both files without describing the actual logic. This scraper maintains outage lifecycle state (`in_progress` / `resolved`) across runs via a `current_outages.json` file in the shared bucket — the same architecture as `italy/edistribuzione` (both are Enel-family ArcGIS FeatureServer scrapers).

**scrape.py** (Airflow `scrape` task):
1. `get_data()` pages through the ArcGIS FeatureServer using `objectid1 > last_id` cursor pagination (2000 records/page) until a page comes back empty.
2. Downloads today's pre-existing raw JSON (if any) and merges it with the new fetch via `update_raw_data()`, tagging each record `outage_ended_today: true/false`.
3. Downloads `current_outages.json` and updates it via `update_current_outages()`: new outage IDs get `ioda_status: "in_progress"` plus `ioda_detection_date`/`ioda_update_date` timestamps; outages still present get `affected_client` bumped to the max seen; outages that dropped out of the new fetch get `ioda_status: "resolved"`.
4. Uploads both the updated raw file and the updated `current_outages.json`.

**post_process.py** (Airflow `post_process` task):
1. Downloads `current_outages.json` and splits it into `resolved` vs. still-`in_progress` via `get_resolved_outages()`.
2. Re-uploads `current_outages.json` containing only the still-`in_progress` records.
3. For each resolved outage, computes duration from `ioda_detection_date`/`ioda_update_date`, and builds a processed record with `country`, `start_utc`, `end_utc`, `duration_(hours)`, `event_category` (`des_cause_en` if it's a string, else `"Unplanned"`), `clients_affected` (`affected_client`), and `area_affected` (`municipality`).
4. Appends these to the day's existing processed-data file (if any) and re-uploads.


## Other Notes

The dataset updates every 5 minutes. Corrected 2026-07-22: the scraper (`spain_edistribucion`) is actually scheduled every 3 hours (`0 */3 * * *` in `airflow/config/scraper_registry.yaml`), not every 4 minutes — this README previously misstated the schedule.

Outage categories include Planned (maintenance) and Unplanned (faults), reflected in `event_category` as the raw `des_cause_en` string when present (e.g. "Unplanned outage"), or `"Unplanned"` as a fallback.