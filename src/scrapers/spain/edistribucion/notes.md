## Data Retrieved

note - string, A brief message to the customer describing the status of the outage.

objectid1 - int, unique integer identifier for the outage event. helpful for tracking an individual outage across multiple 
scraper runs.

cod_cause - string, short code for the outage cause.

latitude - latitude coordinate of the outage location.

municipality - string, town or city where the outage is occuring.

reposition date - string, expected date and time when the power will be restored.

service_des_ca - ?

affected client - int, number of clients affected by the outage.

des_cause_es - ?

cft - string, internal code representing operational zone

des_cause_en - string, description of the outage cause in english.

service_type - string, internal code for category of service

update_time - string, timestamp of the most recent update to the outage record

interruption_date - string, timestamp of when the outage started

service_des_es - ?

des_cause_ca - ?

cd_code - internal code?

objectid - appears to be a second id, but is often null. maybe an old feature?

longitude - longitude coordinate of the location of the outage

service_des_en - string, description of the service issue in english

territory - ?



## Data Retrieval

This dataset comes from e-distribucion, a power provider in spain, which provides live information on current and 
planned power outages in Spain. Data is accessed via the public api that is used to provide data to the live outage map 
on their website.

🔗 https://www.edistribucion.com/en/averias.html

The API endpoint used:

https://ineuportalgis.enel.com/server/rest/services/Hosted/ESP_Prod_power_cut_View/FeatureServer/0/query

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
            "note": "Su suministro está afectado por una incidencia, estamos trabajando en su resolución.",
            "objectid1": 81232447,
            "cod_cause": "A",
            "latitude": 38.44913307,
            "municipality": "Zafra",
            "reposition_date": "03/12/2025 04:00",
            "service_des_ca": "Avaria BT",
            "affected_client": 1,
            "des_cause_es": "Avería",
            "cft": "Zafra",
            "des_cause_en": "Unplanned outage",
            "service_type": "GB",
            "update_time": "03/12/2025 03:45",
            "interruption_date": "02/12/2025 21:52",
            "service_des_es": "Avería BT",
            "des_cause_ca": "Avaria",
            "cd_code": "47210",
            "objectid": null,
            "longitude": -6.42684356,
            "service_des_en": "Unplanned Outage BT",
            "territory": "AND"
        },
        "geometry": {
            "x": -715432.9520059079,
            "y": 4643068.992276251
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