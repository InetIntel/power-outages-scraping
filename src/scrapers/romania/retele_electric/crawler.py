import requests
import pandas as pd
import os
import time
import random

class Romania_ReteleElectric():
    def __init__(self):
        # Retele Electric data for Romania can be found here: https://www.reteleelectrice.ro/en/outages/



        self.name_csv = "romania_retele_electric.csv"
    def retrieve_data(self):
        # This API is not the best so there is no pagination. I think it just gives you all the data at once

        url = "https://services-eu1.arcgis.com/ZugzWQbNk6XT3BMo/arcgis/rest/services/OutagesMapViewLayer/FeatureServer/0/query"

        params = {
            "f": "json",
            "where": "causa_disa_en = 'Accidental'",
            "returnGeometry": "false",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "*",
            "maxRecordCountFactor": 4,
            "orderByFields": "num_cli_di DESC",
            "outSR": 102100,
            "resultOffset": 0,
            "resultRecordCount": 1000,
            "cacheHint": "true",
            # "quantizationParameters": '{"mode":"view","originPosition":"upperLeft","tolerance":1.0583354500042337,"extent":{"xmin":-1e-8,"ymin":-7.081154692251009e-10,"xmax":3312722.8398656575,"ymax":5886664.48646256,"spatialReference":{"wkid":102100,"latestWkid":3857}}}'
        }

        headers = {
        }
        data = []
        results = 1000
        offset = 0
        while True:
            # Retrieve the outage for Unplanned outages
            params["resultRecordCount"] = results
            params["where"] = "causa_disa_en = 'Accidental'"
            params["resultOffset"] = offset

            resp = None

            try: 
                resp = requests.get(url, headers=headers, params=params)
                resp.raise_for_status()
            except Exception as e:
                print("Error:", e)
                break

            features = resp.json().get("features", [])
            # You come to the last page if there is no data
            if len(features) == 0:
                break
            
            # Add the relevant data to the list
            
            data.extend(f.get("attributes", {}) for f in features)
            
            if len(features) < results:
                break
            
            # Set the offset so that you can loop through all the data
            offset += results

            time.sleep(random.uniform(0.5, 1.5))
            # You know you are on the last page of data if it gives you less than the requested results
            
        # Do it again for planned outages
        offset = 0
        while True:
            # Retrieve the outage for Unplanned outages
            params["resultRecordCount"] = results
            params["where"] = "causa_disa_en = 'Planned'"
            params["resultOffset"] = offset
            
            resp = None

            try: 
                resp = requests.get(url, headers=headers, params=params)
                resp.raise_for_status()
            except Exception as e:
                print("Error:", e)
                break

            features = resp.json().get("features", [])
            # You come to the last page if there is no data
            if len(features) == 0:
                break
            
            # Add the relevant data to the list
            
            data.extend(f.get("attributes", {}) for f in features)
            
            if len(features) < results:
                break
            
            # Set the offset so that you can loop through all the data
            offset += results

            time.sleep(random.uniform(0.5, 1.5))
            # You know you are on the last page of data if it gives you less than the requested results

        
        # Temporarily add the data to a pandas dataframe
        page_df = pd.DataFrame(data)
        # write the df to a csv file while checking for duplicate results
        if os.path.exists(self.name_csv):
            existing = pd.read_csv(self.name_csv)
            combined = pd.concat([existing, page_df], ignore_index=True)
            # Drop duplicate rows based on a unique column
            combined = combined.drop_duplicates(subset=['fid0'], keep='last')
        else:
            combined = page_df

        # page_df.to_csv(self.name_csv, mode='a', index=False, header=not os.path.exists(self.name_csv))
        
        combined.to_csv(self.name_csv, index=False)


if __name__ == "__main__":
    outage_class = Romania_ReteleElectric()
    outage_class.retrieve_data()