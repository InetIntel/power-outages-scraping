from utils import BaseScraper
import os
import requests 
from datetime import datetime, timedelta
from utils import print_all_files_recursive
import os
import json
import asyncio
import httpx
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re


class Scraper(BaseScraper):
    # provide some sort of URL. this doesn't need to be exact URL you scrape (it can be dynamic),
    # but just have this here for documentation purposes
    url = "https://cabinet.cherkasyoblenergo.com/api_new/disconn.php"

    """
    This dir_path is very important. Files will be created/uploaded/processed
    according to this dir_path to minio/s3 as well. 
    
    The file will be placed in ./raw/dir_path for raw files or ./processed/dir_path 
    for processed files.

    Structure dir_path as follows: `./your_country/your_power_company/.../...
    """
    dir_path = "./ukraine/cherkasy"

    today = datetime.today().strftime("%Y-%m-%d")
    year = str(datetime.now().year)
    month = str(datetime.now().month).zfill(2)
    concurrent_connections = 3
    semaphore = asyncio.Semaphore(concurrent_connections)

    # date range for queries
    now = datetime.now()
    start_date = now.strftime("%d.%m.%Y")
    end_date = (now + relativedelta(days=1)).strftime("%d.%m.%Y")

    # disconnection types: 0: Planned, 1: Emergency, 2: Outage Schedules
    disconnection_types = [0, 1, 2]
    # department IDs (1-22)
    dept_ids = [i + 1 for i in range(22)]


    async def fetch_single(self, session, disconnection_type, dept_id):
        url = (
            f"{self.url}?op=disconn_by_dept&"
            f"disconn_selector={disconnection_type}&"
            f"n_date={self.start_date}&k_date={self.end_date}&"
            f"dept_id={dept_id}"
        )

        async with self.semaphore:
            try:
                response = await session.get(url)
                if response.status_code == 200:
                    return response.json()
                else:
                    print(
                        f"error fetching dept_id:{dept_id}, type:{disconnection_type}: status {response.status_code}"
                    )
                    return None
            except Exception as e:
                print(
                    f"exception fetching dept_id:{dept_id}, type:{disconnection_type}: {e}"
                )
                return None


    async def fetch_all(self):
        all_data = []

        # disable SSL verification due to certificate issues with the API
        async with httpx.AsyncClient(http2=True, timeout=30.0, verify=False) as client:
            tasks = []
            for disconnection_type in self.disconnection_types:
                for dept_id in self.dept_ids:
                    task = self.fetch_single(client, disconnection_type, dept_id)
                    tasks.append(task)

            results = await asyncio.gather(*tasks)

            # filter out None results and collect data
            all_data = [result for result in results if result is not None]

        if all_data:
            # save raw data
            file_name = f"power_outages.UA.cherkasy.raw.{self.today}.json"
            file_path = os.path.join(f"{self.raw_local_dir}", file_name)

            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(all_data, file, ensure_ascii=False, indent=4)

            print(f"Saved raw data to: {file_path}")
        else:
            print("No data fetched from any endpoint")


    def scrape(self):
        # TODO: implement. make the API call, start selenium, etc.
        # NOTE: make sure to write the file to ./raw/self.dir_path
        # e.g.: ./raw/{self.dir_path}/{self.year}_{date}-brazil-aneel-raw.html"
        async def scrape_sub_func():
            await self.fetch_all()
        asyncio.run(scrape_sub_func())


    def process_single(self, data):
        # Define the date format
        date_format = "%d.%m.%Y %H:%M"
        res = []

        for disconnection_item in data:
            if isinstance(disconnection_item.get("DISCONNECTIONS"), list):
                print(
                    f"skipping empty disconnection item: {disconnection_item.get('DISCONNECTIONS')}"
                )
                continue

            disconnections = disconnection_item.get("DISCONNECTIONS", {})
            if not isinstance(disconnections, dict):
                continue

            for number, disconnection in disconnections.items():
                try:
                    start = disconnection.get("DATE_START", "")
                    end_raw = disconnection.get("DATE_STOP", "")

                    if not start or not end_raw:
                        continue

                    # remove anything after ( in DATE_STOP
                    end = end_raw.split("(")[0].strip()

                    # parse the date strings into datetime objects
                    start_time = datetime.strptime(start, date_format)
                    stop_time = datetime.strptime(end, date_format)

                    # calculate duration in hours
                    duration = (stop_time - start_time).total_seconds() / 3600

                    event_category = disconnection.get("DISCONN_TYPE", "")
                    areas_affected_raw = disconnection.get("ADDRESS", "")

                    # regular expression to find text between <br> tags
                    matches = re.findall(r"<br>(.*?)<br>", areas_affected_raw)
                    cleaned_matches_areas = [
                        match.strip() for match in matches if match.strip()
                    ]

                    # determine event category
                    if event_category == "Планове":
                        category = "Planned"
                    elif event_category in ["Аварійне", "Аварiйне"]:
                        category = "Emergency"
                    else:
                        category = "Outage Schedule"

                    line = {
                        "start": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "end": stop_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "duration_(hours)": "{:.2f}".format(duration),
                        "event_category": category,
                        "country": "Ukraine",
                        "areas_affected": cleaned_matches_areas,
                    }
                    res.append(line)

                except Exception as e:
                    print(f"Error processing disconnection {number}: {e}")
                    continue


    def process(self):
        files_processed = 0

        for root, _, files in os.walk(self.raw_local_dir):
            for filename in files:
                local_path = os.path.join(root, filename)
                processed_file_path = local_path.replace("raw", "processed")
                
                with open(local_path, "r", encoding="utf-8") as file:
                    data = json.load(file)

                res = self.process_single(data)

                with open(processed_file_path, "w", encoding="utf-8") as file:
                    json.dump(res, file, ensure_ascii=False, indent=4)

                print(f"Successfully processed {local_path} to {processed_file_path}")
                files_processed += 1
        
        if files_processed == 0:
            raise RuntimeError(f"[process] nothing processed")