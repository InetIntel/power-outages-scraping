import requests
import pandas as pd
import os
import time
import random

class UK_Scottish_Southern():
    def __init__(self):
        # This one works
        # So, this one has an API with documentation and everything, but the live map uses this API that displays only live outages
        # http://api.sse.com/powerdistribution/network/v3/api/faults. 

        # The API on this website https://data.ssen.co.uk/@ssen-distribution/realtime_outage_dataset
        # gives the data for the SCottish and Southern Electricity Network for the UK which serves 
        # northern Scotland and Southern England. You may need to create an account to see the api data.



        self.name_csv = "scottish_southern_power_outage.csv"
    def retrieve_data(self):
        # This API is not the best so there is no pagination. I think it just gives you all the data at once

        url = "http://api.sse.com/powerdistribution/network/v3/api/faults"
        
        
        
        # Retrieve the outage info
        resp = requests.get(url)

        data = resp.json()
        
        # Temporarily add the data to a pandas dataframe
        page_df = pd.DataFrame(data["faults"])
        # write the df to a csv file while checking for duplicate results
        if os.path.exists(self.name_csv):
            existing = pd.read_csv(self.name_csv)
            combined = pd.concat([existing, page_df], ignore_index=True)
            # Drop duplicate rows based on a unique column
            combined = combined.drop_duplicates(subset=['incidentreference'], keep='last')
        else:
            combined = page_df

        # page_df.to_csv(self.name_csv, mode='a', index=False, header=not os.path.exists(self.name_csv))
        
        combined.to_csv(self.name_csv, index=False)


if __name__ == "__main__":
    sse = UK_Scottish_Southern()
    sse.retrieve_data()