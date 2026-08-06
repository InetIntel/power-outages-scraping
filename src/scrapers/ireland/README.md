# Ireland Power Outage Data (ESB Networks PowerCheck)

Note on the Data Retrieved and the Process of Retrieval

## Data Retrieved ##
outageId - unique integer for the specific outage. Ex: 2694808
outageType - string description of outage: Ex: ["Planned", "Fault", "Restored"]
point - dictionary of longitude, latitude coordinates of the outage. Ex: "{'c': '51.88864,-9.10455'}"
location - string descriptor of town (I think town, but could be some other area type). Ex: Hartnetts Cross
plannerGroup - string descriptor of planner group. Ex: "Bandon,Dunmanway"
numCustAffected - integer of amount of customers without power due to the outage. Ex: 23
startTime - date and time of the start of the outage. Ex: 20/10/2025 15:14
estRestoreTime - date and time of the estimated end of the outage. Ex: 20/10/2025 15:14
statusMessage - generic message about working to restore the power. Ex: We apologise for the loss of supply. We are currently working to repair a fault affecting your premises and will restore power as quickly as possible.
restoreTime - date and time of the end of the outage. Empty if the outage is not Restored. Ex: 20/10/2025 15:14

## Data Retrieval ##
This data comes from https://powercheck.esbnetworks.ie/ which is a live power outage map for Ireland. There is an API I found through inspecting https://powercheck.esbnetworks.ie/list.html.
This API is very easy to use and requires these headers: 

headers = {
            "accept": "application/json",
            "api-subscription-key": "f713e48af3a746bbb1b110ab69113960",
            "captchaoption": "friendlyCaptcha"
        }

The parameters I use are to go through all the pages (if there is more than one).
params = {
            "page": {page},
            "results": 100,
            "sort": 3,
            "order": 1,
            "filter": "",
            "rnd": "0.123456"
        }

> Corrected 2026-07-22: `results` is 100, not 1000. `scrape.py` sets `results_per_page = 100` (its own docstring: "Paginates at 100 results per page"); an earlier draft of this note carried over an unused `results: 1000` value from a dead code path in `crawler.py` that is immediately overwritten before any request is made. Pagination stops per-region on the first `404` response or a page with fewer than 100 results.

The API requires going through each region they have in order to get data for the whole country.
regions = ["Arklow", "Athlone", "Ballina", "Bandon", "Castlebar", 
                        "Cavan", "Clonmel", "Cork", "Drogheda", "Dublin%20Central",
                        "Dublin%20North", "Dundalk", "Dunmanway", "Ennis", "Enniscorthy",
                        "Fermoy", "Galway", "Kilkenny", "Killarney", "Killybegs",
                        "Letterkenny", "Limerick", "Longford", "Mullingar", "Newcastlewest",
                        "Portlaoise", "Roscrea", "Sligo", "Thurles", "Tralee", "Tuam",
                        "Tullamore", "Waterford"]
url = f"https://api.esb.ie/esbn/powercheck/v1.0/plannergroups/{region}/outages"


## Code Process ##
`scrape.py` (Airflow `scrape` task) is the production path: it fetches every region as above, writes the combined raw JSON to `power_outages.IE.esb.raw.<date>.json`, and uploads it via `Uploader` to `ireland/raw/<year>/<month>/`.

`post_process.py` (Airflow `post_process` task) downloads that same raw JSON and re-uploads it unchanged to `ireland/processed/<year>/<month>/` — there is no field parsing, filtering, or deduplication at this stage. It accepts an optional `YYYY-MM-DD` argument to reprocess a past date.

`crawler.py` is an earlier standalone version (pandas/CSV based, `output/ireland_power_outage.csv`) not run by Airflow; kept for reference only.

## Other Notes ##
Data stays for at least 3 hours after the fault is restored, so the API should be called faster than that. The exact refresh rate is still being determined.

Note: the `api-subscription-key` shown above is a real value taken directly from the site's public API calls and is reproduced verbatim in `scrape.py` and `crawler.py`. It is not a secret introduced by this README, but treat it as public/embedded-in-frontend, not a credential to protect.