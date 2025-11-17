import requests
import pandas as pd
import os
import time
import random

class Germany_Fault_Info():
    def __init__(self):
        # This one works
        # So, it is hard to find data in the same style as the UK or Ireland for Germany
        # They do have a live map for the whole country that takes individual outages (reported by customers)
        # and maps them on this website https://xn--strungsauskunft-9sb.de/poweroutage
        # The api url for this was found by inspecting the site. It did not have the best security



        self.name_csv = "storungsauskunft.csv"
    def retrieve_data(self):
        # This API is not the best so there is no pagination. I think it just gives you all the data at once

        url = "https://api-public.stoerungsauskunft.de/api/v1/public/outages"

        
        
        
        params = {"SectorType": "1"}

        headers = {
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "Origin": "https://xn--strungsauskunft-9sb.de",
            "Referer": "https://xn--strungsauskunft-9sb.de/",
        }

        auth = ("frontend", "frontend")

        resp = requests.get(url, params=params, headers=headers, auth=auth)

        data = resp.json()
        
        # Temporarily add the data to a pandas dataframe
        page_df = pd.DataFrame(data)
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
    germ_fi = Germany_Fault_Info()
    germ_fi.retrieve_data()