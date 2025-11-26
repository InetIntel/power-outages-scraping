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
            "results": 1000,
            "sort": 3,
            "order": 1,
            "filter": "",
            "rnd": "0.123456"
        }

The API requires going through each region they have in order to get data for the whole country.
regions = ["Arklow", "Athlone", "Ballina", "Bandon", "Castlebar", 
                        "Cavan", "Clonmel", "Cork", "Drogheda", "Dublin%20Central",
                        "Dublin%20North", "Dundalk", "Dunmanway", "Ennis", "Enniscorthy",
                        "Fermoy", "Galway", "Kilkenny", "Killarney", "Killybegs",
                        "Letterkenny", "Limerick", "Longford", "Mullingar", "Newcastlewest",
                        "Portlaoise", "Roscrea", "Sligo", "Thurles", "Tralee", "Tuam",
                        "Tullamore", "Waterford"]
url = f"https://api.esb.ie/esbn/powercheck/v1.0/plannergroups/{region}/outages"


## Other Notes ##
Data stays for at least 3 hours after the fault is restored, so the API should be called faster than that. The exact refresh rate is still being determined. 