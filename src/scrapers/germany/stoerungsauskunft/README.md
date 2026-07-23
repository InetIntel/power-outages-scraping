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

incidentreference – not observed in the sample record below, but both `post_process.py` and `crawler.py` treat this as the unique key for deduplication (records missing it are kept as-is rather than dropped). Confirm its presence/format against a live response before relying on it.

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

> Corrected 2026-07-22: this section previously described `crawler.py`'s pandas/CSV logic. That is not what runs in production — the Airflow DAG only ever executes `scrape.py` then `post_process.py` (see `airflow/dags/dag_factory.py`), and `crawler.py` is a legacy standalone script. Confirmed: `requirements.txt` lists only `requests`, so `crawler.py` (which imports `pandas`) could not even run inside the built scraper image.

Because the German API delivers all outages in one call, the retrieval process is simple — no pandas, no CSV, no pagination or rate limiting.

**`scrape.py`** (Airflow `scrape` task):
1. Issues a single HTTP GET to the Störungsauskunft outage API with the required headers, basic-auth credentials, and the `SectorType` parameter.
2. Writes the full JSON response as-is to `power_outages.DE.stoerungsauskunft.raw.<date>.json`.
3. Uploads that raw file to the shared volume via `Uploader` at `stoerungsauskunft/raw/<year>/<month>/`.

**`post_process.py`** (Airflow `post_process` task):
1. Downloads that same-day raw JSON file back from the shared volume.
2. Deduplicates records by the `incidentreference` field, keeping the last occurrence of each (records without one are kept as-is).
3. Uploads the deduplicated result to `stoerungsauskunft/processed/<year>/<month>/`.
4. Accepts an optional `YYYY-MM-DD` argument to reprocess a past date.

**`crawler.py`** (legacy, not run by Airflow): an earlier standalone version that accumulates results into a pandas DataFrame and appends to a local CSV (`storungsauskunft.csv`), deduplicating on `incidentreference` the same way. Kept for reference only.

## Other Notes

Outage data is updated continuously as customers report interruptions or operators confirm localized issues.
However, the fixed issues may live in the data for at least 4 hours. Calling the API every 3 hours or so should give high quality data.

One very important note is that each datapoint refers to an outage for an individual customer. Because of this, we will not know
which outages are related to the same failure. It also leads to a lot more data points than other scrapers.

The German system includes both verified operator outages and community-reported events, which may cause short-lived entries.

Timestamps are reported using local German time (CET/CEST).

Many fields may be empty due to the varying level of detail in customer reports.