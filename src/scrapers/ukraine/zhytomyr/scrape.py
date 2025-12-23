import os
import asyncio
from post_process import Process_Zhytomyr
import httpx
from datetime import datetime


class Zhytomyr:
    def __init__(self, concurrent_connections=3):
        self.base_url = "https://www.ztoe.com.ua/unhooking-search.php"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None
        self.year = str(datetime.now().year)
        self.month = str(datetime.now().month).zfill(2)
        self.concurrent_connections = concurrent_connections
        self.semaphore = asyncio.Semaphore(concurrent_connections)

        # department/region IDs to query
        self.rem_ids = ['1', '2', '3', '4', '5', '7', '9', '11', '13', '14', '17', '18', '19', '20', '21', '23', '25']

    def check_folder(self, type):
        self.folder_path = (
                "./ukraine/zhytomyr/" + type + "/" + self.year + "/" + self.month
        )
        os.makedirs(self.folder_path, exist_ok=True)

    async def fetch_single(self, session, rem_id):
        payload = {
            "rem_id": rem_id,
            "naspunkt_id": "0",
            "vulica_id": "0",
            "all": "%EF%EE%EA%E0%E7%E0%F2%E8 %F9%E5 1264 %E7%E0%EF%E8%F1%B3%E2"
        }

        async with self.semaphore:
            try:
                response = await session.post(self.base_url, data=payload)
                if response.status_code == 200:
                    return {
                        "rem_id": rem_id,
                        "html_content": response.text,
                        "status": "success"
                    }
                else:
                    print(
                        f"error fetching rem_id:{rem_id}: status {response.status_code}"
                    )
                    return {
                        "rem_id": rem_id,
                        "html_content": None,
                        "status": "error",
                        "error": f"HTTP {response.status_code}"
                    }
            except Exception as e:
                print(f"exception fetching rem_id:{rem_id}: {e}")
                return {
                    "rem_id": rem_id,
                    "html_content": None,
                    "status": "error",
                    "error": str(e)
                }

    async def fetch_all(self):
        from utils.upload import Uploader

        self.check_folder("raw")

        all_data = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            tasks = []
            for rem_id in self.rem_ids:
                task = self.fetch_single(client, rem_id)
                tasks.append(task)

            results = await asyncio.gather(*tasks)

            # filter out failed results
            all_data = [result for result in results if result.get("status") == "success"]

        if all_data:
            # save individual HTML files (like original crawler)
            for item in all_data:
                rem_id = item.get("rem_id")
                html_content = item.get("html_content")

                if html_content:
                    html_file_name = f"power_outages.UA.zhytomyr.raw.{self.today}.{rem_id}.html"
                    html_file_path = os.path.join(self.folder_path, html_file_name)

                    with open(html_file_path, "w", encoding="utf-8") as file:
                        file.write(html_content)

                    print(f"Saved HTML for rem_id {rem_id}: {html_file_path}")

            # upload to S3
            try:
                uploader = Uploader("ukraine")

                # upload individual HTML files
                for item in all_data:
                    rem_id = item.get("rem_id")
                    if item.get("html_content"):
                        html_file_name = f"power_outages.UA.zhytomyr.raw.{self.today}.{rem_id}.html"
                        html_file_path = os.path.join(self.folder_path, html_file_name)
                        html_s3_path = f"ukraine/zhytomyr/raw/{self.year}/{self.month}/{html_file_name}"
                        uploader.upload_file(html_file_path, html_s3_path)
                        print(f"Uploaded HTML file to S3: {html_s3_path}")
            except Exception as e:
                print(f"Error uploading files to S3: {e}")

            # process the raw data
            process = Process_Zhytomyr(
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
    zhytomyr = Zhytomyr()
    asyncio.run(zhytomyr.scrape())