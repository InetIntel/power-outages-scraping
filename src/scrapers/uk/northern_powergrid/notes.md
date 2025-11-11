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

This API requires an API key for access.
You can obtain one by creating a free account on the Northern Powergrid Open Data Portal and generating an API key from your profile settings.

Once you have your key, include it in each request under the apikey parameter as shown above.

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

The script retrieves outage data 100 records at a time, continuing to request new pages until all records are collected.

For each page:

Data is retrieved via an HTTP GET request to the Opendatasoft API.

Records are stored in a temporary pandas DataFrame.

If a CSV file (northern_powergrid_power_outage.csv) already exists, the new data is concatenated with existing records.

Duplicate handling (based on reference) can be enabled if desired.

The script pauses for 0.5–1.5 seconds between requests to avoid throttling or rate limits.

The loop exits once a response contains fewer than 100 records.

This ensures the resulting CSV always contains the full, most up-to-date set of live outages from Northern Powergrid.

## Other Notes

The dataset updates frequently — typically every 10 minutes.

This dataset does seem to hold onto data from restored outages. It is unknown how long they hold ont them for.

All timestamps are reported in UTC.

Some fields (such as incidentid or custometrmessage) may occasionally be empty or null.