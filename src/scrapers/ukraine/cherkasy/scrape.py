import os
import json
import asyncio
from post_process import Process_Cherkasy
import httpx
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Cherkasy:
    def __init__(self, concurrent_connections=3):
        self.base_url = "https://cabinet.cherkasyoblenergo.com/api_new/disconn.php"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None
        self.year = str(datetime.now().year)
        self.month = str(datetime.now().month).zfill(2)
        self.concurrent_connections = concurrent_connections
        self.semaphore = asyncio.Semaphore(concurrent_connections)

        # date range for queries
        now = datetime.now()
        self.start_date = now.strftime("%d.%m.%Y")
        self.end_date = (now + relativedelta(days=1)).strftime("%d.%m.%Y")

        # disconnection types: 0: Planned, 1: Emergency, 2: Outage Schedules
        self.disconnection_types = [0, 1, 2]
        # department IDs (1-22)
        self.dept_ids = [i + 1 for i in range(22)]

    def check_folder(self, type):
        self.folder_path = (
            "./ukraine/cherkasy/" + type + "/" + self.year + "/" + self.month
        )
        os.makedirs(self.folder_path, exist_ok=True)

    async def fetch_single(self, session, disconnection_type, dept_id):
        url = (
            f"{self.base_url}?op=disconn_by_dept&"
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
        from utils.upload import Uploader

        self.check_folder("raw")

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
            file_path = os.path.join(self.folder_path, file_name)

            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(all_data, file, ensure_ascii=False, indent=4)

            print(f"Saved raw data to: {file_path}")

            # upload to S3
            try:
                uploader = Uploader("ukraine")
                s3_path = f"ukraine/cherkasy/raw/{self.year}/{self.month}/{file_name}"
                uploader.upload_file(file_path, s3_path)
                print(f"Uploaded raw file to S3: {s3_path}")
            except Exception as e:
                print(f"Error uploading raw file to S3: {e}")

            process = Process_Cherkasy(
                self.year,
                self.month,
                self.today,
            )
            process.run()
        else:
            print("No data fetched from any endpoint")

    async def scrape(self):
        await self.fetch_all()


if __name__ == "__main__":
    cherkasy = Cherkasy()
    asyncio.run(cherkasy.scrape())
