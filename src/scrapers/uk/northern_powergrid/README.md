# UK Power Outage Data (Northern Powergrid)

## Data Retrieved

reference – unique alphanumeric identifier for the outage record.
Example: PPCR71687

incidentid – optional unique alphanumeric ID associated with the specific outage event (may be blank in some records).
Example: 7295773

totalconfirmedpowercut – integer count of confirmed power cuts associated with this incident.
Example: 5

powercutcategory – String or integer of the type of power cut. Could be "Unknown", "Safety Interuption", 3, etc. Unknown what the numbers correspond to.
Example: 1

elapsedtime – string indicating how long the outage has been ongoing, typically expressed in days and hours.
Example: 0d 6:10

estimatedtimetillresolution – estimated ISO 8601 timestamp for when power is expected to be restored.
Example: 2025-11-07T13:00:00+00:00

loggedtime – timestamp representing when the outage was logged in the system.
Example: 2025-11-07T09:00:00+00:00

natureofoutage – description of the type or cause of the outage.
Example: Planned Work on System

totalpredictedpowercut – predicted number of customers expected to lose power as part of the outage.
Example: 0

priority – numeric priority level assigned to the outage.
Example: 8

type – type of network or line affected, such as LV (Low Voltage).
Example: LV

customerstagesequence – numeric value indicating the stage of customer restoration. Unknown what the numbers correspond to.
Example: 0

incidentstatus – numeric or categorical code representing the current status of the outage. Unknown what the numbers correspond to.
Example: 6

insertdate – timestamp of when this record was first inserted into the dataset.
Example: 2025-11-07T15:10:30+00:00

updatedate – timestamp of the most recent update to this outage record.
Example: 2025-11-07T15:10:30+00:00

reason – explanation of why the power is out or the purpose of the planned work.
Example: We need to temporarily turn the power off to carry out a permanent repair in the area.

customerstagesequencemessage – message providing context on the restoration sequence or customer stage.
Example: The scheduled work has now been completed.

postcode – postal code(s) for the area affected by the outage.
Example: ['NE70 7PQ']

area – geographic area of the affected region within the Northern Powergrid service area.
Example: North East

lat – latitude coordinate for the outage location.
Example: 55.6257

lng – longitude coordinate for the outage location.
Example: -1.86806

isaffected – binary indicator (0 or 1) showing whether customers are currently affected.
Example: 0

id – internal numeric identifier for the record.
Example: 7311753

label – label field for internal categorization (often empty).
Example: (empty)

incidentsconfigid – configuration ID associated with the outage record (often empty).
Example: (empty)

custometrmessageflag – boolean indicator (True/False) for whether a custom customer message is enabled.
Example: False

custometrmessage – custom estimated restoration message text (often empty).
Example: (empty)

custometrmessageparea – custom message field tied to a geographic area (often empty).
Example: (empty)

configstatus – boolean flag for the configuration status of the outage record.
Example: False

iscustomincident – boolean flag indicating if this is a custom incident record.
Example: False

managecustomincidentsid – identifier used to manage or track custom incidents (often empty).
Example: 0

numberofcalls – number of customer calls received about the outage.
Example: 0

etrstartrange – estimated restoration time range start (may be blank).
Example: (empty)

etrendrange – estimated restoration time range end (may be blank).
Example: (empty)

custometrendrange – custom field for estimated restoration range (often blank).
Example: (empty)

custometrendrangepa – custom field for estimated restoration range by area (often blank).
Example: (empty)

duration – numeric value for total outage duration in minutes.
Example: 370

geopoint – geographic point as a JSON object with longitude and latitude keys.
Example: {'lon': -1.86806, 'lat': 55.6257}

## Data Retrieval

This dataset comes from Northern Powergrid (UK) via their Open Data Portal
, which provides live information on power cuts across Northern England.

🔗 https://northernpowergrid.opendatasoft.com/explore/dataset/live-power-cuts-data/information/

The API endpoint used is provided by the Opendatasoft platform, which returns live JSON responses for current outages.

url = "https://northernpowergrid.opendatasoft.com/api/explore/v2.1/catalog/datasets/live-power-cuts-data/records"


Parameters used:

params = {
    "limit": 100,      # number of records per request
    "offset": offset,  # pagination offset
    "apikey": apikey   # required API key for authenticated access
}

Authentication

This API is documented as requiring an API key for access — you can obtain one by creating a free account on the Northern Powergrid Open Data Portal and generating an API key from your profile settings.

**Correction 2026-07-22: neither `scrape.py` nor `crawler.py` actually sends one.** `scrape.py` sends `"apikey": ""` (empty string). `crawler.py` has the same empty value with its own comment admitting the gap: `apikey = ""  # Need this from the administrators`, and an earlier comment: `# Need an IODA API key! The current one is my personal one`. Whether the endpoint tolerates an empty key (some Opendatasoft public catalogs allow anonymous reads) or the scraper is silently failing/rate-limited without one has not been verified — treat "authentication is configured" as false until an actual key is wired in and confirmed working.

Example JSON Response
{
  "results": [
    {
      "reference": "PPCR71687",
      "incidentid": 7295773,
      "totalconfirmedpowercut": 5,
      "powercutcategory": 1,
      "elapsedtime": "0d 6:10",
      "estimatedtimetillresolution": "2025-11-07T13:00:00+00:00",
      "loggedtime": "2025-11-07T09:00:00+00:00",
      "natureofoutage": "Planned Work on System",
      "reason": "We need to temporarily turn the power off to carry out a permanent repair in the area.",
      "postcode": ["NE70 7PQ"],
      "area": "North East",
      "lat": 55.6257,
      "lng": -1.86806,
      "isaffected": 0
    }
  ]
}

Code Process

> Corrected 2026-07-22: this section previously described `crawler.py`'s pandas/CSV logic and didn't mention `post_process.py` at all. The Airflow DAG only ever executes `scrape.py` then `post_process.py` (see `airflow/dags/dag_factory.py`); `crawler.py` is a legacy standalone script. Confirmed: `requirements.txt` lists only `requests`, so `crawler.py` (which imports `pandas`) could not run inside the built scraper image.

**`scrape.py`** (Airflow `scrape` task):
1. Retrieves outage data 100 records at a time from the Opendatasoft API, paging via `offset`, until a page returns fewer than 100 records or is empty.
2. Unlike `uk/national_grid`'s scraper, **no deduplication happens here** — records are simply concatenated (`all_records.extend(results)`).
3. Writes the combined records as `power_outages.GB.northern_powergrid.raw.<date>.json` to a local temp path, uploads via `Uploader` to `northern_powergrid/raw/<year>/<month>/`, then deletes the local temp file.

**`post_process.py`** (Airflow `post_process` task): downloads that same-day raw JSON and re-uploads it unchanged as `northern_powergrid/processed/<year>/<month>/power_outages.GB.northern_powergrid.processed.<date>.json` — no field parsing, filtering, or deduplication happens here either. Accepts an optional `YYYY-MM-DD` argument to reprocess a past date.

**`crawler.py`** (legacy, not run by Airflow): an earlier standalone version that accumulates results into a pandas DataFrame and appends to a local CSV (`northern_powergrid_power_outage.csv`). Its deduplication line (`combined.drop_duplicates(subset=['reference'], keep='last')`) is commented out, so even this legacy version does not dedupe. Kept for reference only.

## Other Notes

The dataset updates frequently — typically every 10 minutes.

This dataset does seem to hold onto data from restored outages. It is unknown how long they hold ont them for.

All timestamps are reported in UTC.

Some fields (such as incidentid or custometrmessage) may occasionally be empty or null.