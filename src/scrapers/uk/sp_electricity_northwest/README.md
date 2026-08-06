# Electricity North West Power Outage Data
## Data Retrieved

FaultLabel – string description of the outage label or general category (e.g., “Live power cut”).
Example: Live power cut

Type – category of fault record, typically indicating the data group (e.g., “CurrentFault”, "ResovedFault", "TodaysPlannedWorks").
Example: CurrentFault

Icon – UI icon name used on the public-facing website to visually represent the fault.
Example: icon-warning

ShowViewOnMapCTA – boolean flag indicating whether the outage includes a “View on Map” button on the website.
Example: False

UnderReview – boolean value indicating if the outage is under active review.
Example: False

AdditionalFaultInfo – textual explanation of the cause or background of the fault.
Example: “The power cut in your area has been caused by an unexpected incident with the overhead cable that provides electricity to your property.”

UpdateInfo – textual field sometimes containing progress updates from SP Energy Networks about restoration efforts.
Example: (empty string if not provided)

CTAs – list of dictionaries containing call-to-action links displayed on the website (each includes an Icon, Text, and Url).
Example:

[
  {
    "Icon": "icon-arrow-right",
    "Text": "What to do in a power cut",
    "Url": "/power-cuts/helpful-tips/tips-to-help-you-during-a-power-cut/"
  },
  {
    "Icon": "icon-arrow-right",
    "Text": "I'm involved in this power cut",
    "Url": "/about-us/contact-us/report-a-power-cut-105/"
  }
]


faultNumber – unique string identifier assigned to each outage.
Example: INC 125280849

multipleFaultNumbers – string or list of additional fault IDs if the outage is associated with multiple faults.
Example: (empty or null)

date – ISO 8601 timestamp indicating when the outage record was created or last updated.
Example: 2025-11-10T15:42:56

region – string name of the affected region or area.
Example: Selside And Fawcett Forest, South Lakeland

faultType – descriptive name for the fault classification (e.g., “Current Fault”).
Example: Current Fault

faultStatus – short text indicating the current status of the fault.
Example: We're on site

previousFaultStatus – prior recorded status value before the most recent update.
Example: We're on site

consumersOff – integer representing the estimated number of customers currently without power.
Example: 5

estimatedTimeOfRestoration – ISO 8601 timestamp estimate for full restoration of power.
Example: 2025-11-10T23:00:00

estimatedTimeOfRestorationMajority – timestamp for when power is expected to be restored to the majority of affected customers.
Example: 2025-11-10T23:00:00

information – optional message field with general or situational information.
Example: (empty)

actualTimeOfRestoration – timestamp for when the outage was actually resolved (if completed).
Example: (empty if ongoing)

outageCentrePoint – dictionary containing the latitude and longitude of the outage center point.
Example: {"lat": 54.365899, "lng": -2.726621}

outageLocations – text field listing additional outage locations or specific sites.
Example: (empty)

AffectedPostcodes – comma-separated list of postcodes affected by the outage.
Example: "LA8 9BF, LA8 9LE"

UnderReviewStatusTimeCheck – boolean value used internally to indicate review timing.
Example: False

WebTMSFaultType – short internal classification of the fault type.
Example: O/HM

addressMpanList – list or string of MPANs (Meter Point Administration Numbers) associated with the outage.
Example: (empty or null)

## Data Retrieval

This dataset comes from Electricity North West, which provides live information on ongoing and recent power cuts through their website and public API.

🔗 Website: https://www.enwl.co.uk/power-cuts/power-cuts-power-cuts-live-power-cut-information-fault-list/fault-list/

The public website dynamically loads data through the following API endpoint:

url = "https://www.enwl.co.uk/api/power-outages/search"

Parameters used
params = {
    "pageSize": 100,              # number of records per page
    "pageNumber": page_number,    # pagination control
    "includeCurrent": True,        # include currently active faults
    "includeResolved": True,       # include resolved outages
    "includeTodaysPlanned": False,
    "includeFuturePlanned": False,
    "includeCancelledPlanned": False,
}

Corrected 2026-07-22: `includeTodaysPlanned` is `False` in both `scrape.py` and `crawler.py` — this README previously had it as `True`. Today's planned outages are currently excluded from what this scraper collects.

Authentication

This API does not currently require authentication or an API key.
Requests can be made directly to the endpoint with the parameters shown above.

The API returns a paginated JSON structure with a list of outage items:

{
  "Items": [
    {
      "FaultLabel": "Live power cut",
      "Type": "CurrentFault",
      "Icon": "icon-warning",
      ...
    }
  ]
}

Code Process

> Corrected 2026-07-22: this section previously described `crawler.py`'s pandas/CSV logic and didn't mention `post_process.py`. The Airflow DAG only ever executes `scrape.py` then `post_process.py` (see `airflow/dags/dag_factory.py`); `crawler.py` is a legacy standalone script. Confirmed: `requirements.txt` lists only `requests`, so `crawler.py` (which imports `pandas`) could not run inside the built scraper image.

**`scrape.py`** (Airflow `scrape` task):
1. Requests outage data 100 records at a time (`pageSize`/`pageNumber`) until a page returns fewer than 100 records or is empty.
2. Deduplicates in-memory by `faultNumber` using a Python `set` (not pandas).
3. Writes the deduplicated records as `power_outages.GB.sp_electricity_northwest.raw.<date>.json` to a local temp path, uploads via `Uploader` to `sp_electricity_northwest/raw/<year>/<month>/`, then deletes the local temp file.

**`post_process.py`** (Airflow `post_process` task): downloads that same-day raw JSON and re-uploads it unchanged as `sp_electricity_northwest/processed/<year>/<month>/power_outages.GB.sp_electricity_northwest.processed.<date>.json` — no field parsing, filtering, or further deduplication happens here. Accepts an optional `YYYY-MM-DD` argument to reprocess a past date.

**`crawler.py`** (legacy, not run by Airflow): an earlier standalone version that accumulates results into a pandas DataFrame and appends to a local CSV (`sp_electricity_northwest.csv`), deduplicating on `faultNumber` with `keep="last"`. Its own comments admit `# Need an IODA API key! The current one is my personal one` even though no API key parameter is actually sent — likely a stale comment copied from another scraper in this family (see `uk/northern_powergrid`, where the equivalent comment is accurate). Kept for reference only.

## Other Notes

The dataset is live and updates frequently throughout the day.

Including both “current” and “resolved” outages allows for simple time-based analysis or event frequency tracking.

This should be called every 10 to 12 hours (Resolved data is still available for up to 17 hours (likely 24 hours)).

Some text fields (e.g., UpdateInfo, information) may be empty if no updates are available.

All timestamps are provided in UTC (ISO 8601 format).