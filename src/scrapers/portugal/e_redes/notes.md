# Portugal E-Redes Outage Dataset
## Data Retrieved

zipcode – postal code representing the geographic area associated with the outage record.
Example: 1100-001

municipality – name of the municipality where the outage is occurring.
Example: Lisboa

extractiondatetime – timestamp indicating when the outage record was extracted from the E-Redes dataset.
This represents the “data freshness” rather than the outage start time.
Example: 2025-12-03T17:59:00+00:00

municipalitycode – numeric or alphanumeric code identifying the municipality within Portugal’s administrative system.
Example: 1106

interrupcao_ativa – indicator specifying whether there is an active power interruption in this geographic area.
Typically encoded as 1 (active interruption) or 0 (no active interruption). This is my best guess based on the limited data.
It is worth pursuing further whether this is a binary or lists the number of active interruptions in that area.
Example: 1

## Data Retrieval

This dataset comes from E-Redes, the main electricity distribution operator for Portugal.
The data is published through their official Open Data Portal on the Opendatasoft platform.

🔗 Dataset information page:
https://e-redes.opendatasoft.com/explore/dataset/outages-per-geography/information/

The API endpoint used is the standard Opendatasoft “v2.1 records” endpoint, which returns paginated JSON:

https://e-redes.opendatasoft.com/api/explore/v2.1/catalog/datasets/outages-per-geography/records

Request Parameters

The script uses the following query parameters:

params = {
    "limit": limit,     # number of records per page (20)
    "offset": offset,   # pagination offset
}


E-Redes does not require an API key for this dataset, and all records are publicly accessible.

The API returns responses in the form:

{
  "results": [
    {
      "zipcode": "1100-001",
      "municipality": "Lisboa",
      "extractiondatetime": "2025-12-03T17:59:00+00:00",
      "municipalitycode": "1106",
      "interrupcao_ativa": 1
    }
  ]
}

Code Process

The script retrieves outage data in batches of 20 records per request, looping until no additional pages remain.

For each page:

A request is sent to the Opendatasoft API using limit and offset.

The JSON results are loaded into a temporary pandas DataFrame.

If the CSV file (portugal_e_redes.csv) already exists, the script loads the existing file and concatenates it with the new records.

The combined DataFrame is saved back to the CSV.

A short randomized delay (0.5–1.5 seconds) is included between requests to avoid excessive API traffic.

The loop ends when:

the API returns zero results, or

the number of returned records is less than the requested limit.

This process ensures that the final CSV contains all available outage-related geographic records from the E-Redes public feed.

## Other Notes

The E-Redes dataset represents geographic areas with active or inactive interruptions, not individual outage IDs.

interrupcao_ativa = 1 indicates one or more active interruptions in the area at the time of extraction I think. This needs to be explored further.

The extractiondatetime reflects the timestamp when the Open Data Portal last updated the dataset, not when the outage started.

Because this dataset updates frequently, polling the API regularly (e.g., every 15 minutes) provides the most accurate representation of ongoing outages. The website says that the data updates every 15 minutes.

Since the dataset is geographic, multiple rows may refer to different zip codes or municipalities experiencing activity simultaneously.