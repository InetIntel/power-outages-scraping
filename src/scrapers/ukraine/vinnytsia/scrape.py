import os
import asyncio
from post_process import Process_Vinnytsia
import httpx
from datetime import datetime
import lxml.html


class Vinnytsia:
    def __init__(self, concurrent_connections=3):
        self.base_url = "https://voe.com.ua/disconnection"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None
        self.year = str(datetime.now().year)
        self.month = str(datetime.now().month)
        self.concurrent_connections = concurrent_connections
        self.semaphore = asyncio.Semaphore(concurrent_connections)

        # regions to query
        self.regions = [
            "23",
            "25",
            "26",
            "27",
            "29",
            "30",
            "31",
            "32",
            "33",
            "35",
            "36",
            "37",
            "38",
            "39",
            "41",
            "42",
            "43",
            "45",
            "46",
            "47",
            "48",
            "50",
            "51",
            "52",
            "53",
            "55",
            "56",
            "57",
        ]

        # types: planned and emergency
        self.types = ["planned", "emergency"]

    def check_folder(self, type):
        self.folder_path = (
            "./ukraine/vinnytsia/" + type + "/" + self.year + "/" + self.month.zfill(2)
        )
        os.makedirs(self.folder_path, exist_ok=True)

    async def fetch_page(self, session, url):
        try:
            response = await session.get(url)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Error fetching {url}: Status {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception fetching {url}: {e}")
            return None

    async def fetch_with_pagination(self, session, region, type):
        url = f"{self.base_url}/{type}/{self.year}/{self.month}/{region}"
        all_content = []
        page_num = 1

        while url:
            print(f"fetching {type} for region {region}, page {page_num}...")
            html_content = await self.fetch_page(session, url)

            if html_content is None:
                break

            all_content.append(html_content)

            try:
                tree = lxml.html.fromstring(html_content)
                next_page_link = tree.xpath('//a[@rel="next-page"]/@href')

                if next_page_link:
                    # make absolute URL if it's relative
                    next_url = next_page_link[0]
                    if next_url.startswith("/"):
                        url = f"https://voe.com.ua{next_url}"
                    elif next_url.startswith("http"):
                        url = next_url
                    else:
                        url = f"{self.base_url}/{next_url}"
                    page_num += 1
                else:
                    url = None
            except Exception as e:
                print(f"Error parsing next page link: {e}")
                url = None

        # combine all pages into one HTML
        return "\n".join(all_content) if all_content else None

    async def fetch_single(self, session, region, type):
        async with self.semaphore:
            combined_html = await self.fetch_with_pagination(session, region, type)
            if combined_html:
                return region, type, combined_html
            return None

    async def fetch_all(self):
        from utils.upload import Uploader

        self.check_folder("raw")

        all_data = []

        # disable SSL verification due to potential certificate issues
        async with httpx.AsyncClient(
            http2=True, timeout=30.0, verify=False, follow_redirects=True
        ) as client:
            tasks = []
            for region in self.regions:
                for type in self.types:
                    task = self.fetch_single(client, region, type)
                    tasks.append(task)

            results = await asyncio.gather(*tasks)

            all_data = [result for result in results if result is not None]

        if all_data:
            # save each region+type HTML to a separate file
            uploader = None
            try:
                uploader = Uploader("ukraine")
            except Exception as e:
                print(f"error initializing uploader: {e}")

            for region, type, html_content in all_data:
                file_name = (
                    f"power_outages.UA.vinnytsia.raw.{self.today}.{region}.{type}.html"
                )
                file_path = os.path.join(self.folder_path, file_name)

                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(html_content)

                print(
                    f"saved raw data for region {region}, type {type} to: {file_path}"
                )

                # upload to S3
                if uploader:
                    s3_path = f"ukraine/vinnytsia/raw/{self.year}/{self.month.zfill(2)}/{file_name}"
                    try:
                        uploader.upload_file(file_path, s3_path)
                        print(f"uploaded raw file to S3: {s3_path}")
                    except Exception as e:
                        print(
                            f"error uploading raw file for region {region}, type {type} to S3: {e}"
                        )

            process = Process_Vinnytsia(
                self.year,
                self.month.zfill(2),
                self.today,
            )
            process.run()
        else:
            print("no data fetched from any region/type combination")

    async def scrape(self):
        await self.fetch_all()


if __name__ == "__main__":
    vinnytsia = Vinnytsia()
    asyncio.run(vinnytsia.scrape())
