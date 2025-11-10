Note on the Data Retrieved and the Process of Retrieval
## Data Retrieved ##

id – internal index number for the dataset record, added by the source or API. This is not global. It is only for this data pull.
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

The script iterates through pages of results (1,000 records at a time) until no additional records are returned.

For each page:

Data is retrieved via an HTTP GET request to the API.

Records are temporarily stored in a pandas DataFrame.

New records are appended to an existing CSV file (national_grid_power_outage.csv).

Duplicate records (based on Incident ID) are dropped to ensure only the latest record per incident remains.

The script pauses briefly (0.5–1.5s) between calls to avoid rate limiting.

This ensures the CSV contains all current and recent outage events from the National Grid’s feed.

## Other Notes ##

The dataset is live and frequently updated every 5 minutes by the National Grid.

We should be polling data either every 5 minutes (just after the data update) or faster.

All data is in GMT time