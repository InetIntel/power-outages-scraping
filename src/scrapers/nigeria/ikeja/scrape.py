import os
import asyncio
from post_process import Process_Ikeja
import httpx
from datetime import datetime


class Ikeja:
    def __init__(self, concurrent_connections=1):
        self.url = "https://www.ikejaelectric.com/cnn/"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None
        self.year = str(datetime.now().year)
        self.month = str(datetime.now().month).zfill(2)
        self.concurrent_connections = concurrent_connections
        self.semaphore = asyncio.Semaphore(concurrent_connections)

    def check_folder(self, type):
        self.folder_path = (
            "./nigeria/ikeja/" + type + "/" + self.year + "/" + self.month
        )
        os.makedirs(self.folder_path, exist_ok=True)

    async def fetch(self):
        from utils.upload import Uploader

        self.check_folder("raw")
        async with self.semaphore:
            try:
                async with httpx.AsyncClient(http2=True, timeout=30.0) as client:
                    response = await client.get(self.url)
            except httpx.ConnectError as e:
                if "CERTIFICATE_VERIFY_FAILED" in str(e):
                    print(f"Certificate error")
                    async with httpx.AsyncClient(
                        http2=True, timeout=30.0, verify=False
                    ) as client:
                        response = await client.get(self.url)
                else:
                    raise

            if response.status_code == 200:
                file_name = "power_outages.NG.ikeja.raw." + self.today + ".html"
                file_path = os.path.join(self.folder_path, file_name)

                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(response.text)

                try:
                    uploader = Uploader("nigeria")
                    s3_path = f"nigeria/ikeja/raw/{self.year}/{self.month}/{file_name}"
                    uploader.upload_file(file_path, s3_path)
                    print(f"Uploaded raw file to S3: {s3_path}")
                except Exception as e:
                    print(f"Error uploading raw file to S3: {e}")

                process = Process_Ikeja(
                    self.year,
                    self.month,
                    self.today,
                )
                process.run()
            else:
                print(f"Status code: {response.status_code}")

    async def scrape(self):
        await self.fetch()


if __name__ == "__main__":
    ikeja = Ikeja()
    asyncio.run(ikeja.scrape())
