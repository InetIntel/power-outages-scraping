## Data Retrieved

outageid – unique integer identifying the specific outage.
Example: 5882759

outagetype – string description of the outage type, such as "Fault" or "Planned".
Example: Fault

starttime – timestamp of when the outage began.
Example: "5:51 AM, 10 Nov"

estrestorefulldatetime – estimated date and time for full restoration of power.
This may occasionally contain placeholder text when no estimate is available.
Example: "Not available - Update to follow"

postcode – partial or full postal code representing the affected area.
Example: BT49 0

numcustaffected – integer representing the number of customers without power due to this outage.
Example: 31

statusmessage – general message from NIE Networks about the current outage status or restoration progress.
Example: "The repair team is working to resolve the problem."

updatedtimestamp – timestamp of the last update from the API for this outage record.
Example: "7:29 PM, 10 Nov"

## Data Retrieval

This dataset comes from Northern Ireland Electricity Networks (NIE Networks) via their Open Data Portal, which provides live information on current and recent faults across Northern Ireland.

🔗 https://nienetworks.opendatasoft.com/explore/dataset/nie-networks-network-faults/information/

The API endpoint used is provided by the Opendatasoft platform, which delivers JSON responses for live datasets.

url = "https://nienetworks.opendatasoft.com/api/explore/v2.1/catalog/datasets/nie-networks-network-faults/records"

Parameters used:
params = {
    "limit": 100,      # number of records per request
    "offset": offset,  # pagination offset
    "apikey": apikey   # required API key for authenticated access
}


Authentication:
This API requires an API key for access. You can obtain one by creating a free account on the NIE Networks Open Data Portal and generating an API key from your user profile.

Once you have the key, include it in each request under the apikey parameter as shown above.

The API returns paginated JSON responses with a list of current outage records, following the structure:

{
  "results": [
    {
      "outageid": 5882759,
      "outagetype": "Fault",
      "starttime": "5:51 AM, 10 Nov",
      "estrestorefulldatetime": "Not available - Update to follow",
      "postcode": "BT49 0",
      "numcustaffected": 31,
      "statusmessage": "The repair team is working to resolve the problem.",
      "updatedtimestamp": "7:29 PM, 10 Nov"
    }
  ]
}

Code Process

The script retrieves outage data 100 records at a time, continuing to request new pages until all records are collected.

For each page:

Data is retrieved via an HTTP GET request to the Opendatasoft API.

Records are temporarily stored in a pandas DataFrame.

If a CSV file already exists (northern_ireland_power_outage.csv), the script appends new data and concatenates it into a combined DataFrame.

Duplicate records can optionally be removed by comparing a unique identifier (e.g. outageid).

The script pauses for 0.5–1.5 seconds between requests to avoid rate limiting or throttling by the API.

Once all pages are retrieved (fewer than 100 results returned), the process stops.

This process ensures that the resulting CSV contains the full, up-to-date set of outages available from the NIE Networks live feed.

## Other Notes

The dataset is live and updates approximately every 30 minutes.

Because some outages are temporary or quickly resolved, data should be retrieved at least every 30 minutes to avoid missing transient faults.

All timestamps are reported in local time for Northern Ireland (GMT or BST depending on daylight savings).

The estrestorefulldatetime field may be empty or contain placeholder text for active outages that do not yet have an estimated restoration time.
