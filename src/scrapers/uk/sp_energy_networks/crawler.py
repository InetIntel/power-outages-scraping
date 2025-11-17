import requests
import pandas as pd
import os
import time
import random

class UK_SP_Energy():
    def __init__(self):
        # Need an IODA API key! The current one is my personal one
        # This 

        # The API on this website https://spenergynetworks.opendatasoft.com/explore/dataset/distribution-network-live-outages/information/
        # The api call can be found here https://spenergynetworks.opendatasoft.com/api/explore/v2.1/console
        # gives the data for the Power Networks Utility in the UK serving the North and west part of the country
        self.name_csv = "sp_energy_networks_power_outage.csv"
    def retrieve_data(self):
        # Retrieve up to 100 pieces of data per data pull then requests more if there are more to be had.

        limit = 100
        offset = 0
        url = "https://spenergynetworks.opendatasoft.com/api/explore/v2.1/catalog/datasets/distribution-network-live-outages/records"
        apikey = "" # Need this from the administrators


        while True:
            params = {
                "limit": limit,
                "offset": offset,
                "apikey": apikey
            }
            
            # Retrieve the outage info
            resp = requests.get(url, params=params)

            # You come to the last page if there is no records
            if len(resp.json()["results"]) == 0:
                break

            data = resp.json()
            
            # Temporarily add the data to a pandas dataframe
            page_df = pd.DataFrame(data["results"])
            # write the df to a csv file while checking for duplicate results
            if os.path.exists(self.name_csv):
                existing = pd.read_csv(self.name_csv)
                combined = pd.concat([existing, page_df], ignore_index=True)
                # Drop duplicate rows based on a unique column
                combined = combined.drop_duplicates(subset=['incidentreference'], keep='last')
            else:
                combined = page_df

            # page_df.to_csv(self.name_csv, mode='a', index=False, header=not os.path.exists(self.name_csv))
            # print(len(page_df))
            
            combined.to_csv(self.name_csv, index=False)
            offset += limit

            time.sleep(random.uniform(0.5, 1.5))
            # You know you are on the last page of data if it gives you less than the requested results
            if len(page_df) < limit:
                break

            # Debug statements for the Docker container
            # print(f"Calling the API for {region}")
        # print("Finished")

if __name__ == "__main__":
    sp_energy = UK_SP_Energy()
    sp_energy.retrieve_data()