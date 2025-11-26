SP Energy Networks Power Outage Data
Data Retrieved

fault_id – unique identifier assigned to each power outage record.
Example: INCD-905355-f

licence_area – string describing the licensed electricity distribution area under SP Energy Networks’ responsibility.
Example: SP Manweb

region – name of the local region or district where the outage occurred.
Example: GWYNEDD MENAI

status – current status of the outage, such as “Awaiting” or “In Progress”.
Example: Awaiting

planned – boolean value indicating whether the outage was planned (True) or unplanned (False).
Example: True

planned_outage_start_date – timestamp for when a planned outage is scheduled to begin.
Example: 2025-11-03T22:00:00+00:00

date_of_reported_fault – timestamp indicating when the outage or fault was first reported.
Example: 2025-10-23T09:40:22+00:00

etr – estimated time of restoration for power supply.
Example: 2025-11-04T04:00:00+00:00

voltage – classification of the voltage level affected by the outage (e.g., LV for Low Voltage, HV for High Voltage).
Example: LV

postcode_sector – list or array containing the postcode sectors affected by the outage.
Example: ['LL74 8']

Data Retrieval

This dataset comes from SP Energy Networks via their Open Data Portal
, which provides live information on power outages across their distribution areas in the north and west of the United Kingdom.

🔗 https://spenergynetworks.opendatasoft.com/explore/dataset/distribution-network-live-outages/information/

The dataset is hosted on the Opendatasoft platform, which offers public access to live API endpoints returning JSON-formatted data.

The API endpoint used:

url = "https://spenergynetworks.opendatasoft.com/api/explore/v2.1/catalog/datasets/distribution-network-live-outages/records"

Parameters used:
params = {
    "limit": 100,      # number of records per request
    "offset": offset,  # pagination offset for multiple pages
    "apikey": apikey   # required API key for authenticated access
}

Authentication:

This API requires an API key for access.
You can obtain one by creating a free account on the SP Energy Networks Open Data Portal and generating an API key from your user profile.

Once your key is created, include it in the request parameters under apikey, as shown above.

API Response Structure:

The API returns paginated JSON responses with a list of current and recent outage records:

{
  "results": [
    {
      "fault_id": "INCD-905355-f",
      "licence_area": "SP Manweb",
      "region": "GWYNEDD MENAI",
      "status": "Awaiting",
      "planned": true,
      "planned_outage_start_date": "2025-11-03T22:00:00+00:00",
      "date_of_reported_fault": "2025-10-23T09:40:22+00:00",
      "etr": "2025-11-04T04:00:00+00:00",
      "voltage": "LV",
      "postcode_sector": ["LL74 8"]
    }
  ]
}

Code Process

The retrieval script downloads outage data in batches of 100 records per request, continuing to fetch new pages until all available records have been retrieved.

For each page:

Data is retrieved via an HTTP GET request to the Opendatasoft API.

Each batch of results is converted to a pandas DataFrame.

If the CSV file (sp_energy_networks_power_outage.csv) already exists, the new data is concatenated to it.

Duplicate records are removed by comparing the unique incidentreference field (or equivalent unique ID).

A short randomized delay (0.5–1.5 seconds) is used between requests to prevent potential throttling by the API.

The process automatically terminates once a page returns fewer than 100 results.

This ensures the resulting CSV contains all current and recent power outage records available through SP Energy Networks’ live API feed.

## Other Notes

The dataset is live and updated frequently throughout the day. It updates every 5 minutes.

Because outages can be short-lived or resolved quickly, it is recommended to retrieve data at least once per 5 minutes to maintain a complete record.

All timestamps are reported in UTC using ISO 8601 format.