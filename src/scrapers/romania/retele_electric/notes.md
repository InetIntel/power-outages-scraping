# Germany Power Outage Data (Störungsauskunft)
## Data Retrieved

id – unique integer identifying the specific reported outage.
Example: 5975365

operatorId – numeric identifier for the energy network operator responsible for the affected area.
Example: 120

subsection – additional internal subdivision of the operator’s network area.
This field may be empty depending on the record.
Example: (empty)

type – integer representing the type or classification of the outage event.
Example: 1

origin – integer describing the origin of the report (customer report, operator detection, automated signal, etc.).
Example: 3

geoType – numeric code representing the type of geographic information provided.
Example: 1

dateStart – timestamp indicating when the outage event began.
Example: "11/13/2025 09:46:20"

dateEnd – estimated or actual timestamp for when the outage is expected to be resolved.
Example: "11/13/2025 15:50:00"

lastUpdate – timestamp of the most recent update associated with this outage record.
Example: "11/13/2025 10:00:25"

postalCode – postal code of the affected area.
Example: 24976

city – city or municipality where the outage has occurred.
Example: Handewitt

district – smaller administrative district or locality.
This field may be empty.
Example: (empty)

street – the street associated with the reported outage.
This field may be empty.
Example: (empty)

radius – radius (in meters) of the affected area when a circular mapped area is used. This is for their internal map.
Example: 500

CoordinateSystemType – identifier for the coordinate reference system used for the outage location.
Example: "Unknown"

coordinates – string containing longitude and latitude of the outage location, comma-separated.
Example: "9.383424335717224,54.7452532333094"

liveInfo – real-time details about the outage.
This field may be empty.

comments – any operator-submitted notes or customer comments associated with the outage.
Example: (empty)

definition – an optional description or definition associated with the outage.
Example: (empty)

social – Unknown what this refers to.
Example: (empty)

socialText – associated social media text when available.
Example: (empty)

isOutageInArea – boolean indicating whether the outage directly affects the mapped area.
Example: False

isFixed – boolean describing whether the outage has been resolved.
Example: False

SectorType – integer indicating the category of infrastructure, such as electricity (1).
Example: 1

operatorName – name of the network operator responsible for the outage.
Example: Schleswig-Holstein Netz AG

containerShape – describes the geometric container for the affected area (may be empty).
Example: (empty)

countryCode – two-letter country code for the outage location.
Example: DE

idPublic – public identifier used for external reference.
Example: (empty)

internal – internal operator field used for system management.
Example: 0

houseNr – house number associated with the outage event (may be empty).
Example: (empty)

photo – link or reference to an associated photo if submitted (usually empty).
Example: (empty)

isUserCommentDisabled – boolean determining whether user comments are permitted.
Example: False

includeInMap – boolean indicating whether the outage is visible in the public outage map.
Example: (empty)

internalLampId – internal lamp or streetlight identifier when applicable.
Example: (empty)

## Data Retrieval

This dataset comes from Störungsauskunft, Germany’s national outage reporting platform used by grid operators and consumers. It aggregates live customer-reported and operator-confirmed outages across Germany.

🔗 https://störungsauskunft.de
 (internationalized domain: xn--strungsauskunft-9sb.de)

Although the site does not provide a public open data portal, all outage information is retrieved from an internal API used by their public interactive map.
This API was identified through browser developer tools.

API Endpoint Used
https://api-public.stoerungsauskunft.de/api/v1/public/outages


The API returns all current outages in a single request (no pagination).

Parameters Used
params = {
    "SectorType": "1"      # 1 = electricity outages
}

Authentication

The Störungsauskunft API uses basic authentication, but the credentials are openly embedded in the public website’s JavaScript:

Username: frontend

Password: frontend

These credentials are used to access public outage data only.

Headers

To match the behavior of the official website and avoid rejection, the following headers are required:

Standard User-Agent string

Origin: https://xn--strungsauskunft-9sb.de

Referer: https://xn--strungsauskunft-9sb.de/

Response Structure

The API returns a list of outage objects in the following format:

[
  {
    "id": 5975365,
    "operatorId": 120,
    "subsection": "",
    "type": 1,
    "origin": 3,
    "geoType": 1,
    "dateStart": "11/13/2025 09:46:20",
    "dateEnd": "11/13/2025 15:50:00",
    "lastUpdate": "11/13/2025 10:00:25",
    "postalCode": 24976,
    "city": "Handewitt",
    "district": "",
    "street": "",
    "radius": "Unknown",
    "CoordinateSystemType": "Unknown",
    "coordinates": "9.383424335717224,54.7452532333094",
    "liveInfo": "",
    "comments": "",
    "definition": "",
    "social": false,
    "socialText": "",
    "isOutageInArea": false,
    "isFixed": false,
    "SectorType": 1,
    "operatorName": "Schleswig-Holstein Netz AG",
    "containerShape": "",
    "countryCode": "DE",
    "idPublic": "",
    "internal": 0,
    "houseNr": "",
    "photo": "",
    "isUserCommentDisabled": false,
    "includeInMap": "",
    "internalLampId": ""
  }
]

Code Process

Because the German API delivers all outages in one call, the retrieval process is simpler than the UK or Ireland versions.

For each run:

The script issues a single HTTP GET request to the Störungsauskunft outage API.

This request includes:

The required headers

Authentication credentials

The SectorType parameter

The full list of outages is returned in a single JSON response.

Results are stored in a pandas DataFrame.

If a CSV file (storungsauskunft.csv) already exists, the new results are appended and combined.

Duplicate records can be removed by specifying a unique identifier field.

The final combined dataset is written to the output CSV.

Unlike the UK and Ireland APIs, there is no pagination and no rate limiting, so no delays are required between requests.

This process ensures you maintain a full historical record of all outages displayed on the Störungsauskunft map.

## Other Notes

Outage data is updated continuously as customers report interruptions or operators confirm localized issues.
However, the fixed issues may live in the data for at least 4 hours. Calling the API every 3 hours or so should give high quality data. Documentation says it updates every 15 minutes.

One very important note is that each datapoint refers to an outage for an individual customer. Because of this, we will not know
which outages are related to the same failure. It also leads to a lot more data points than other scrapers.

The German system includes both verified operator outages and community-reported events, which may cause short-lived entries.

Timestamps are reported using local German time (CET/CEST).

Many fields may be empty due to the varying level of detail in customer reports.