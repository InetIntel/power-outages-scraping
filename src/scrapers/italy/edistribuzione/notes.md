  ## Data Retrieved
  
fid0 - ?, seems to be null often/always

note - string, customer facing message about status of the outage

objectid1 - int, unique identifier for the outage event

causa_interruzione - (English: interruption cause), string, internal code representing cause of outage

num_cli_disalim - (English: number of customers without power), int, number of customers affected by outage

dataultimoaggiornamento - (English: last update date), string, timestamp when outage event was most recently updated

descrizione_territoriale - (English: territorial description), string, territory associated with the outage

data_prev_ripristino - (English: estimated restoration date/time), string, timestamp of estimated outage restoration time

provincia - (English: province), string, province where the outage is occurring

cod_cs - string, internal code?

regione - (English: region), string, region where the outage is located

cft - string, internal code?

comune - int, ?

data_interruzione - (English: interruption start date), string, timestamp of when the outage began

latitudine - float, latitude coordinate of the outage location

x - always null?

id_interruzione - (English: interruption id), int, another outage event id?

y - always null?

causa_disalimentazione - (English: disconnection cause), string, human readable description of outage cause (in italian)

fid2 - int, ?

longitudine - float, longitude coordinate of the outage location

objectid - always null, another outage event id, possibly legacy identifier


## Data Retrieval

This dataset comes from e-distribuzione, a power provider in italy, which provides live information on current 
power outages in Italy. Data is accessed via the public api that is used to provide data to the live outage map 
on their website.

🔗 https://www.e-distribuzione.it/interruzione-corrente-primo.html

The API endpoint used:

https://ineuportalgis.enel.com/server/rest/services/Hosted/ITA_power_cut_map_layer_View/FeatureServer/0/query

Parameters used:
params = {
            "f": "json",
            "where": f"objectid1 > {last_id}",
            "outFields": "*",
            "returnGeometry": "true",
            "orderByFields": "objectid1 ASC",
            "resultRecordCount": 2000,
        }

Authentication:

This dataset is publicly accessible and does not require an API key.
However, requests should be rate-limited (e.g., 0.5–1.5 seconds between calls) to avoid throttling.

API Response Structure:

Each API response contains a JSON payload with an array of outage records in the features field. Each individual
outage then also contains an attributes and a geometry field:

{
  "features": [
    {
        "attributes": {
            "fid0": null,
            "note": "",
            "objectid1": 39928511,
            "causa_interruzione": "LV",
            "num_cli_disalim": 238,
            "dataultimoaggiornamento": "03/12/2025 08:00",
            "descrizione_territoriale": "ASSEMINI",
            "data_prev_ripristino": "03/12/2025 15:00",
            "provincia": "Cagliari",
            "cod_cs": "D7102123574",
            "regione": "Sardegna",
            "cft": "D000AA0",
            "comune": 92003,
            "data_interruzione": "03/12/2025 08:00",
            "latitudine": 39.28735568,
            "x": null,
            "id_interruzione": 1011886783,
            "y": null,
            "causa_disalimentazione": "Lavoro Programmato",
            "fid2": 0,
            "longitudine": 9.01587807,
            "objectid": null
        },
        "geometry": {
            "x": 1003642.9552714042,
            "y": 4762916.792617008
        },
    },
    ...
  ]
}

Code Process

scrape.py:

Refer to spain/naturgy scraper.


post_process.py:

Refer to spain/naturgy scraper.


## Other Notes

The dataset updates every 5 minutes, so the scraper is scheduled for every 4 minutes to make sure all data is captured.

Outage categories include Planned (maintenance) and Unplanned (faults).