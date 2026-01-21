## Data Retrieved

OBJECTID - unique integer identifier for the outage event. helpful for tracking an individual outage across multiple 
scraper runs.

ZONA - (English: Area), string value

TIPO_GRUPO - (English: Group Type), integer value

ID_GRUPO - (English: Group ID), String value

ID_GRUPO_INCI - (English: Groupd ID INCI?), Integer value

PROVINCIA - (English: Province), Province of Spain where the outage is taking place.

TIPO - (English: Type), integer value representing the category of the outage. (1: Planned, 2: Unplanned)

CENTRO - (English: Center), integer value

FECHA_DETECCION - (English: Detection Date), integer value representing when the outage was detected. Number of 
milliseconds since 1970 in UTC time.

FECHA_RESOLUCION - (English: Resolution Date), integer value representing when the outage is expected to be resolved. 
Number of milliseconds since 1970 in UTC time.

ESTADO - (English: State), string value representing current state of the outage. Seems like it's almost always 
set to "En resolución" (in resolution).

INS_AFECTADA - ?

INS_ORIGEN - ?

NIV_TEN - ?

TIPO_INC - ?

CLIENTES_AFECTADOS - (English: Affected Customers), integer value representing the number of clients affected 
by the outage.

DURACION - (English: Duration), Duration of the outage. All the outages being returned by this api are ongoing, so it 
seems like this value is almost always set to null.

created_date - integer value representing when the outage event was created. Number of milliseconds since 1970.

last_edited_date - integer value representing when the outage event was last edited. Number of milliseconds since 1970. 
All outages are updated together every 5 minutes. 

FECHA_FICHERO - (English: File Date)

CLIENTES_AFECTADOS_TXT - (English: Affected Customers Txt), string value representing the number of clients affected 
by the outage.

LastFile - integer value

CENTRO_OPERACIONES - (English: Operations Center)

## Data Retrieval

This dataset comes from Naturgy, a power provider in spain, which provides live information on current and planned power outages in Spain.
Data is accessed via the public api that is used to provide data to the live outage map on Naturgy's website.

🔗 https://www.ufd.es/estado-del-servicio/

The API endpoint used:

https://gisoperaciones.ufd.es/server/rest/services/Averias/Avisos_VistaPublica/FeatureServer/0/query

Parameters used:
params = {
            "f": "json",
            "where": f"OBJECTID > {last_id}",
            "outFields": "*",
            "returnGeometry": "true",
            "outSR": 4326,
            "orderByFields": "OBJECTID ASC",
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
            "OBJECTID": 296041,
            "ZONA": "N",
            "TIPO_GRUPO": 0,
            "ID_GRUPO": "611036415",
            "ID_GRUPO_INCI": 0,
            "PROVINCIA": "A Coruña",
            "TIPO": 1,
            "CENTRO": 6110,
            "FECHA_DETECCION": 1764409800000,
            "FECHA_RESOLUCION": -2209165200000,
            "ESTADO": "En resolución",
            "INS_AFECTADA": "1115:40208762",
            "INS_ORIGEN": "",
            "NIV_TEN": "B",
            "TIPO_INC": "",
            "CLIENTES_AFECTADOS": 83,
            "DURACION": null,
            "created_date": 1764412510000,
            "last_edited_date": 1764436510000,
            "FECHA_FICHERO": 1764436140000,
            "CLIENTES_AFECTADOS_TXT": "83",
            "LastFile": 1,
            "CENTRO_OPERACIONES": "6110"
        },
        "geometry": {
            "x": -8.376589294067683,
            "y": 43.19723757667924
        },
    },
    ...
  ]
}

Code Process

scrape.py:

This code first requests records using public api. Stored as a list of dicts.

Then pull the "current_outages.json" file from minio. This is a file that tracks currently ongoing outages. This is 
helpful for outages that span multiple scraper runs so that each outage can be treated as a single event even 
if it is seen multiple times. Once an outage has ended, it is then removed from this file and handled by the post 
processor. 

If an outage is already in the "current_outages.json" file and is still being seen by the api, then it is mostly left 
unchanged, but if the number of clients increased in the newest api call then this value is updated in the 
current outages file. 

If an outage was just seen for the first time in the newest api call, then it is added to the 
current outages file and given a tag "ioda_status" = "in_progress". This tag tells the post processor that this outage 
is still ongoing and to ignore it for now. 

And lastly, if an outage is contained in the current outage file but was not seen by the most recent api call, then 
the outage has ended. This outage in the current outages file has its "ioda_status" tag updated to "resolved". This 
tells the post processor that this outage has ended and the data can now be processed and removed from the current 
outage file.

After "current_outages.json" has been updated, it is then uploaded to minio (replacing its previous iteration).

If this is the first time today that this scraper has been run, then the newly scraped raw data is downloaded locally to 
the docker container as a json file then uploaded to minio. If the scraper has already been run today, then the raw 
data file for current day is retrieved from minio, new raw outage data is added to file, then updated raw data file 
is uploaded to minio. Since this scraper is run very frequently (every 4 minutes), condensing all the raw data to one 
json file per day makes it more manageable to find the data you're looking for in minio.


post_process.py:

This script starts by downloading "current_outages.json" from minio (description above in scrape.py notes). It then 
iterates through each of the outages in this file and checks the "ioda_status" value. An outage marked as "in_progress" 
is still ongoing and is ignored. An outage marked as "resolved" is completed and can not be processed and removed 
from the file.

This script only stores one processed data file per day in minio. So if this file already exists in minio, then it 
is retrieved so that we can be appended to. If it does not exist then we start with an empty list.

Once we've iterated through all the outages in "current_outages.json" and pulled the appropriate data for post 
processing. These outages are then run through a function that formats the outages for IODA, adds them to the list of 
previously existing processed outages for today if there were any, then uploads the processed data file to minio
(replacing any previous iteration of it).

The updated "current_outages,json" file is also uploaded to minio. The resolved outages have been removed from it.

## Other Notes

The dataset updates every 5 minutes, so the scraper is scheduled for every 4 minutes to make sure all data is captured.

Outage categories include Planned (maintenance) and Unplanned (faults).

Timestamps follow UTC (millisecond count since 1970).