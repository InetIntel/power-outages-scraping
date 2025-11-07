import requests
import pandas as pd
import os
import time
import random

class Ireland_API():
    def __init__(self):
        # The API on this website https://powercheck.esbnetworks.ie/list.html requires a region by region view of the power outages
        self.regions = ["Arklow", "Athlone", "Ballina", "Bandon", "Castlebar", 
                        "Cavan", "Clonmel", "Cork", "Drogheda", "Dublin%20Central",
                        "Dublin%20North", "Dundalk", "Dunmanway", "Ennis", "Enniscorthy",
                        "Fermoy", "Galway", "Kilkenny", "Killarney", "Killybegs",
                        "Letterkenny", "Limerick", "Longford", "Mullingar", "Newcastlewest",
                        "Portlaoise", "Roscrea", "Sligo", "Thurles", "Tralee", "Tuam",
                        "Tullamore", "Waterford"]
        # self.regions = ["Dublin%20North"]
        self.name_csv = "output/ireland_power_outage.csv"
    def retrieve_data(self):
        # Retrieve up to 1000 pieces of data from each region
        # This will need to be changed to stop if less data is given
        # or go to the next page if there is more data to retrieve
        params = {
            "page": 1,
            "results": 1000,
            "sort": 3,
            "order": 1,
            "filter": "",
            "rnd": "0.123456"
        }
        # These headers will retrieved via the page source of the url (https://powercheck.esbnetworks.ie/list.html)
        headers = {
            "accept": "application/json",
            "api-subscription-key": "f713e48af3a746bbb1b110ab69113960",
            "captchaoption": "friendlyCaptcha"
        }
        # Retrieve the data region by region and add it to a master data structure

        results = 100

        for region in self.regions:
            page = 1
            while True:
                params = {
                    "page": page,
                    "results": results,
                    "sort": 3,
                    "order": 1,
                    "filter": "",
                    "rnd": "0.123456"
                }
                url = f"https://api.esb.ie/esbn/powercheck/v1.0/plannergroups/{region}/outages"
                # Retrieve the outage info for that region
                resp = requests.get(url, headers=headers, params=params)

                # You come to the last page if there is a 404 status
                if resp.status_code == 404:
                    break

                data = resp.json()
                
                # Check if there is any data
                if "outageDetail" not in data:
                    continue
                # Temporarily add the data to a pandas dataframe
                page_df = pd.DataFrame(data['outageDetail'])
                # write the df to a csv file
                page_df.to_csv(self.name_csv, mode='a', index=False, header=not os.path.exists(self.name_csv))
                page += 1

                time.sleep(random.uniform(0.5, 1.5))
                # You know you are on the last page of data if it gives you less than the requested results
                if len(page_df) < results:
                    break

            # Debug statements for the Docker container
            # print(f"Calling the API for {region}")
        # print("Finished")

if __name__ == "__main__":
    eire = Ireland_API()
    eire.retrieve_data()