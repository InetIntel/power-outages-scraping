import requests
import pandas as pd
import os
import time
import random

class UK_Power_Networks():
    def __init__(self):
        # Need an IODA API key! The current one is my personal one
        # This 

        # The API was found by inspecting this website https://www.enwl.co.uk/power-cuts/power-cuts-power-cuts-live-power-cut-information-fault-list/fault-list/
        # There appears to be no security restrictions.
        # I wonder if doing include resolved will request every power outage that has ever happened for them

        self.name_csv = "sp_electricity_northwest.csv"
    def retrieve_data(self):
        # Retrieve up to 100 pieces of data per data pull then requests more if there are more to be had.

        limit = 100
        page_number = 1
        url = "https://www.enwl.co.uk/api/power-outages/search"

        while True:
            params = {
                "pageSize": limit,
                "pageNumber": page_number,
                "includeCurrent": True,
                "includeResolved": True,
                "includeTodaysPlanned": False,
                "includeFuturePlanned": False,
                "includeCancelledPlanned": False,
            }
            
            # Retrieve the outage info
            resp = requests.get(url, params=params)

            # You come to the last page if there is no records
            if len(resp.json()["Items"]) == 0:
                break

            data = resp.json()
            
            # Temporarily add the data to a pandas dataframe
            page_df = pd.DataFrame(data["Items"])
            # write the df to a csv file while checking for duplicate results
            if os.path.exists(self.name_csv):
                existing = pd.read_csv(self.name_csv)
                combined = pd.concat([existing, page_df], ignore_index=True)
                # Drop duplicate rows based on a unique column
                combined = combined.drop_duplicates(subset=['faultNumber'], keep='last')
            else:
                combined = page_df

            # page_df.to_csv(self.name_csv, mode='a', index=False, header=not os.path.exists(self.name_csv))
            # print(len(page_df))
            
            combined.to_csv(self.name_csv, index=False)
            page_number += 1

            time.sleep(random.uniform(0.5, 1.5))
            # You know you are on the last page of data if it gives you less than the requested results
            if len(page_df) < limit:
                break

        # print("Finished")

if __name__ == "__main__":
    pow_net = UK_Power_Networks()
    pow_net.retrieve_data()