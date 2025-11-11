## Data Retrieved

title – short description of the affected area or region for the outage.
Example: OX26 Area

reference – unique alphanumeric identifier for the outage record.
Example: RZ0261

loggedAtUtc – timestamp (UTC) when the outage was logged in the system.
Example: 2025-11-03T21:10:00Z

type – indicates the type of network affected (e.g., LV = Low Voltage, HV = High Voltage).
Example: LV

location – JSON object containing the latitude and longitude of the outage location.
Example: {'latitude': 51.89897680644274, 'longitude': -1.152619509147509}

estimatedRestorationTimeUtc – estimated UTC timestamp for when power is expected to be restored.
Example: 2025-11-04T01:00:00Z

message – customer-facing message describing the current outage status and providing contact information.
Example: "We’re sorry for the loss of supply. We currently have a fault affecting the areas listed. Our engineers are on site working hard to get the power back on as quickly as they can. If you need more information, please call us on 105 or send us a message on Facebook or Twitter and quote reference 'RZ0261'."

affectedAreas – list of partial or full postal codes representing the areas affected by the outage.
Example: ['OX26 6JJ', 'OX26 6JS', 'OX26 6JT', 'OX26 6JU', 'OX26 6JW']

uri – direct API URL providing detailed information for the individual outage record.
Example: http://api.sse.com/powerdistribution/network/v3/api/fault/RZ0261

depotCode – internal depot or regional service code handling the outage.
Example: 42

primaryNrn – internal network reference number for the affected high-voltage network.
Example: 4605

hvFeederNrn – high-voltage feeder reference number associated with the outage.
Example: 15

transformerNrn – transformer reference number involved in the outage event.
Example: 10

lvFeederNrn – low-voltage feeder reference number, if applicable.
Example: 2

jobStatus – alphanumeric code describing the current job status of the outage (e.g., I for In Progress).
Example: I

jobSubType – numeric or alphanumeric value indicating a subtype or classification of the job. The related categories are unknown.
Example: 07

transformerType – internal code representing the type of transformer affected.
Example: U

mergedTo – identifier showing if the outage has been merged into another incident. May be blank.
Example: (blank)

customerCount – number of customers affected by the outage.
Example: 19

estimatedArrivalOnSiteUtc – estimated UTC time for engineer arrival on site. May be blank.
Example: (blank)

engineerOnSiteTimeUtc – timestamp for when engineers were confirmed on site. May be blank.
Example: (blank)

## Data Retrieval

This dataset comes from Scottish and Southern Electricity Networks (SSEN) via their live API, which provides real-time information about current electricity faults across southern England and northern Scotland.

🔗 https://data.ssen.co.uk/@ssen-distribution/realtime_outage_dataset

The live outage data is also available directly through the SSEN API endpoint:

url = "http://api.sse.com/powerdistribution/network/v3/api/faults"


The API returns all current outage data in a single JSON payload. No pagination is required.

The response follows the structure:

{
  "faults": [
    {
      "title": "OX26 Area",
      "reference": "RZ0261",
      "loggedAtUtc": "2025-11-03T21:10:00Z",
      "type": "LV",
      "location": {
        "latitude": 51.89897680644274,
        "longitude": -1.152619509147509
      },
      "estimatedRestorationTimeUtc": "2025-11-04T01:00:00Z",
      "message": "We’re sorry for the loss of supply...",
      "affectedAreas": ["OX26 6JJ", "OX26 6JS"],
      "uri": "http://api.sse.com/powerdistribution/network/v3/api/fault/RZ0261",
      "depotCode": 42,
      "primaryNrn": 4605,
      "hvFeederNrn": 15,
      "transformerNrn": 10,
      "lvFeederNrn": 2,
      "jobStatus": "I",
      "jobSubType": "07",
      "transformerType": "U",
      "mergedTo": "",
      "customerCount": 19,
      "estimatedArrivalOnSiteUtc": "",
      "engineerOnSiteTimeUtc": ""
    }
  ]
}

Code Process

The script sends a single HTTP GET request to the SSEN API and retrieves all current outage records.

Process overview:

Retrieves the outage data via requests.get(url)

Converts the JSON response into a pandas DataFrame

If an existing CSV file (scottish_southern_power_outage.csv) is present, new data is appended and duplicates are dropped based on the reference column

The combined DataFrame is saved as a CSV file for archival and analysis

Since the API does not require pagination, the script only makes a single request per run.

A short randomized delay (0.5–1.5 seconds) can optionally be added between requests to avoid overloading the endpoint if run in rapid succession.

## Other Notes

This dataset is live and updates continuously as new faults are reported or resolved. I do not know the data refresh rate.

Each request retrieves only current active outages (not historical).

Timestamps are reported in UTC.

Some fields, such as engineerOnSiteTimeUtc, may be empty if the information has not yet been logged.