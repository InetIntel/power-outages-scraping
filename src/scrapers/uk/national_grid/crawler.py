import requests
import pandas as pd
import os
import time
import random

class UK_National_Grid():
    def __init__(self):
        # The API on this website https://connecteddata.nationalgrid.co.uk/dataset/live-power-cuts/resource/292f788f-4339-455b-8cc0-153e14509d4d
        # gives the data for the National Grid Utility in the UK serving the middle of the country
        self.name_csv = "national_grid_power_outage.csv"
    def retrieve_data(self):
        # Retrieve up to 1000 pieces of data per data pull then requests more if there are more to be had.

        limit = 1000
        offset = 0
        url = "https://connecteddata.nationalgrid.co.uk/api/3/action/datastore_search"
        
        while True:
            params = {
                "resource_id": "292f788f-4339-455b-8cc0-153e14509d4d",
                "limit": limit,
                "offset": offset
            }
            
            # Retrieve the outage info
            resp = requests.get(url, params=params)

            # You come to the last page if there is no records
            if len(resp.json()["result"]["records"]) == 0:
                break

            data = resp.json()
            
            # Temporarily add the data to a pandas dataframe
            page_df = pd.DataFrame(data["result"]["records"])
            # write the df to a csv file
            if os.path.exists(self.name_csv):
                existing = pd.read_csv(self.name_csv)
                combined = pd.concat([existing, page_df], ignore_index=True)
                # Drop duplicate rows based on a unique column
                combined = combined.drop_duplicates(subset=['Incident ID'], keep='last')
            else:
                combined = page_df

            # combined.to_csv(self.name_csv, mode='a', index=False, header=not os.path.exists(self.name_csv))
            
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
    nat_grid = UK_National_Grid()
    nat_grid.retrieve_data()