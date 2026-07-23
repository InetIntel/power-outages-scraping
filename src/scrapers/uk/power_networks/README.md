# UK Power Outage Data (UK Power Networks)

## Data Retrieved

incidentreference – unique alphanumeric identifier for the outage record.
Example: INCD-23344-O

powercuttype – categorical label describing whether the outage is Planned or Unplanned.
Example: Planned

creationdatetime – timestamp (ISO 8601 format) of when the outage record was created.
Example: 2025-10-14T15:19:51

nocallsreported – integer number of calls received from customers reporting the outage.
Example: 1

incidentscount – total number of individual incidents grouped under this outage record.
Example: 0

nocustomeraffected – estimated number of customers affected by this outage.
Example: 0

postcodesaffected – semicolon-separated list of postal code regions where outages are reported or planned.
Example: NR10 3;NR10 5;NR12 7;NR14 8

restoredincidents – number of incidents within the record that have already been restored.
Example: (empty)

unplannedincidents – number of unplanned faults associated with the outage.
Example: (empty)

plannedincidents – number of planned maintenance outages associated with the outage.
Example: (empty)

incidenttypetbcestimatedfriendlydescription – textual field for estimated outage time or restoration window, if available.
Example: 10 Nov 11:30 - 12:30

incidentdescription – short description of the outage type or operational note.
Example: (empty)

fullpostcodedata – semicolon-separated list of all full postcodes affected by the outage.
Example: NR105JA;NR127NS;NR127NR;NR105LH;NR105HZ;NR105JD;NR127NT;NR148SQ

incidentcategorycustomerfriendlydescription – customer-facing description of the incident category, explaining why the outage occurred.
Example:

“We're carrying out planned work in your area. For our engineers to carry it out safely they need to turn the power off. We're doing this work as it's essential to provide reliable electricity supplies to your area. We're sorry for any inconvenience caused and thank you for your patience.”

incidentcategory – integer code representing the general category of the incident (e.g., Planned, Fault, or Unknown).
Example: 28

incidenttypename – plain text description of the outage classification.
Example: Planned

incidenttype – numeric code for the type of outage corresponding to the classification system used by UK Power Networks.
Example: 3

incidentpriority – integer value representing the priority level of the outage.
Example: 12

statusid – numeric code for the current outage status (e.g., 5 = resolved, 6 = ongoing)(I think).
Example: 5

restoreddatetime – timestamp indicating when power was fully restored.
Example: 2025-11-10T11:45:16.89

planneddate – timestamp for when the planned outage was scheduled to begin.
Example: 2025-11-10T09:00:00

receiveddate – timestamp for when this incident was first received by the reporting system.
Example: 2025-11-10T09:03:49

noplannedcustomers – estimated number of customers planned to be affected during maintenance.
Example: 42

plannedincidentreason – textual description of why the outage was planned.
Example:

“We're carrying out planned work in your area. For our engineers to carry it out safely they need to turn the power off. We're doing this work as it's essential to provide reliable electricity supplies to your area. We're sorry for any inconvenience caused and thank you for your patience.”

message – optional message field for internal or public outage communications.
Example: (empty)

mainmessage – customer-facing message summarizing the impact of the outage and expected restoration time.
Example:

“The electricity supply to your premises may currently be affected by planned work. You should have received a letter explaining this. We hope to be able to restore your supplies by 10-NOV-2025 12:00. Please accept our sincere apologies for any inconvenience this is causing.”

geopoint – dictionary containing longitude and latitude coordinates for the affected area.
Example: {'lon': 1.26203, 'lat': 52.58471}

estimatedrestorationdate – timestamp estimating when full restoration is expected.
Example: 2025-11-10T12:00:00

operatingzone – textual label identifying the local operating zone or region of the network.
Example: NORWICH

## Data Retrieval

This dataset comes from UK Power Networks (UKPN), which provides live information on current and planned power outages in southeastern England.
Data is accessed via the UK Power Networks Open Data Portal, powered by Opendatasoft.

🔗 https://ukpowernetworks.opendatasoft.com/explore/dataset/ukpn-live-faults/information/

The API endpoint used:

https://ukpowernetworks.opendatasoft.com/api/explore/v2.1/catalog/datasets/ukpn-live-faults/records

Parameters used:
params = {
    "limit": 100,     # number of records per request
    "offset": offset  # pagination offset
}

Authentication:

This dataset is publicly accessible and does not require an API key.
However, requests should be rate-limited (e.g., 0.5–1.5 seconds between calls) to avoid throttling.

API Response Structure:

Each API response contains a JSON payload with an array of outage records in the results field:

{
  "results": [
    {
      "incidentreference": "INCD-23344-O",
      "powercuttype": "Planned",
      "creationdatetime": "2025-10-14T15:19:51",
      ...
    }
  ]
}

Code Process

> Corrected 2026-07-22: this section previously described `crawler.py`'s pandas/CSV logic and didn't mention `post_process.py`. The Airflow DAG only ever executes `scrape.py` then `post_process.py` (see `airflow/dags/dag_factory.py`); `crawler.py` is a legacy standalone script. Confirmed: `requirements.txt` lists only `requests`, so `crawler.py` (which imports `pandas`) could not run inside the built scraper image.

**`scrape.py`** (Airflow `scrape` task):
1. Requests records 100 at a time using pagination (`limit` + `offset`) until a page returns fewer than 100 records or is empty.
2. Deduplicates in-memory by `incidentreference` using a Python `set` (not pandas).
3. Writes the deduplicated records as `power_outages.GB.power_networks.raw.<date>.json` to a local temp path, uploads via `Uploader` to `power_networks/raw/<year>/<month>/`, then deletes the local temp file.

**`post_process.py`** (Airflow `post_process` task): downloads that same-day raw JSON and re-uploads it unchanged as `power_networks/processed/<year>/<month>/power_outages.GB.power_networks.processed.<date>.json` — no field parsing, filtering, or further deduplication happens here. Accepts an optional `YYYY-MM-DD` argument to reprocess a past date.

**`crawler.py`** (legacy, not run by Airflow): an earlier standalone version that accumulates results into a pandas DataFrame and appends to a local CSV (`power_networks_power_outage.csv`), deduplicating on `incidentreference` with `keep="last"`. Kept for reference only.

## Other Notes

The dataset updates approximately every 10 minutes.

Outage categories include Planned (maintenance) and Unplanned (faults).

Timestamps follow UTC (ISO 8601 format).