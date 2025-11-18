import os
import asyncio
from post_process import Process_Khmelnytsky
import httpx
from datetime import datetime, timedelta


class Khmelnytsky:
    def __init__(self, concurrent_connections=3):
        self.base_url = "https://hoe.com.ua/shutdown/eventlist"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None
        self.year = str(datetime.now().year)
        self.month = str(datetime.now().month).zfill(2)
        self.concurrent_connections = concurrent_connections
        self.semaphore = asyncio.Semaphore(concurrent_connections)

        # regions to query
        self.regions = ["4", "12", "17", "21", "23", "24"]

        # date range for queries
        now = datetime.now()
        one_day_later = now + timedelta(days=1)
        self.formatted_start_date = now.strftime("%d.%m.%Y")
        self.formatted_end_date = one_day_later.strftime("%d.%m.%Y")

    def check_folder(self, type):
        self.folder_path = (
            "./ukraine/khmelnytsky/" + type + "/" + self.year + "/" + self.month
        )
        os.makedirs(self.folder_path, exist_ok=True)

    async def fetch_single(self, session, region):
        form_data = {
            "TypeId": "2",
            "PageNumber": "1",
            "RemId": region,
            "DateRange": f"{self.formatted_start_date} - {self.formatted_end_date}",
            "X-Requested-With": "XMLHttpRequest",
        }

        async with self.semaphore:
            try:
                response = await session.post(self.base_url, data=form_data)
                if response.status_code == 200:
                    return region, response.text
                else:
                    print(
                        f"error fetching region: {region} w/ status: {response.status_code}"
                    )
                    return None
            except Exception as e:
                print(f"exception fetching region:{region}: w/ error: {e}")
                return None

    async def fetch_all(self):
        from utils.upload import Uploader

        self.check_folder("raw")

        all_data = []

        # disable SSL verification due to potential certificate issues
        async with httpx.AsyncClient(http2=True, timeout=30.0, verify=False) as client:
            tasks = []
            for region in self.regions:
                task = self.fetch_single(client, region)
                tasks.append(task)

            results = await asyncio.gather(*tasks)

            # filter out None results
            all_data = [result for result in results if result is not None]

        if all_data:
            # save each region's HTML to a separate file
            uploader = None
            try:
                uploader = Uploader("ukraine")
            except Exception as e:
                print(f"error initializing uploader: {e}")

            for region, html_content in all_data:
                file_name = (
                    f"power_outages.UA.khmelnytsky.raw.{self.today}.{region}.html"
                )
                file_path = os.path.join(self.folder_path, file_name)

                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(html_content)

                print(f"saved raw data for region {region} to: {file_path}")

                # upload to S3
                if uploader:
                    s3_path = (
                        f"ukraine/khmelnytsky/raw/{self.year}/{self.month}/{file_name}"
                    )
                    try:
                        uploader.upload_file(file_path, s3_path)
                        print(f"uploaded raw file to S3: {s3_path}")
                    except Exception as e:
                        print(
                            f"error uploading raw file for region {region} to S3: {e}"
                        )

            process = Process_Khmelnytsky(
                self.year,
                self.month,
                self.today,
            )
            process.run()
        else:
            print("no data fetched from any region")

    async def scrape(self):
        await self.fetch_all()


if __name__ == "__main__":
    khmelnytsky = Khmelnytsky()
    asyncio.run(khmelnytsky.scrape())
