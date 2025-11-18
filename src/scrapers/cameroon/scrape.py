import os
import json
import asyncio
import httpx
from datetime import datetime


class CameroonScraper:
    def __init__(self, concurrent_connections=3):
        self.url = "https://alert.eneo.cm/ajaxOutage.php"
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.year = str(datetime.now().year)
        self.month = str(datetime.now().month).zfill(2)
        self.concurrent_connections = concurrent_connections
        self.semaphore = asyncio.Semaphore(concurrent_connections)

        self.regions = {
            'adamaoua': '1',
            'centre': '2',
            'douala': 'X-22',
            'est': '3',
            'extreme_nord': '4',
            'littoral': '5',
            'ouest': '6',
            'nord': '7',
            'nord_ouest': '8',
            'sud': '9',
            'sud_ouest': '10',
            'yaounde': 'X-1'
        }

    async def fetch_region(self, region_name, region_code):

        async with self.semaphore:
            try:
                async with httpx.AsyncClient(
                        http2=True,
                        timeout=30.0,
                        follow_redirects=True
                ) as client:
                    response = await client.post(
                        self.url,
                        data={'region': region_code},
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.3',
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    )
            except (httpx.ConnectError, httpx.SSLError) as e:
                print(f"[{region_name.upper()}] SSL error")
                try:
                    async with httpx.AsyncClient(
                            http2=True,
                            timeout=30.0,
                            verify=False,
                            follow_redirects=True
                    ) as client:
                        response = await client.post(
                            self.url,
                            data={'region': region_code},
                            headers={
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.3',
                                'Content-Type': 'application/x-www-form-urlencoded',
                                'X-Requested-With': 'XMLHttpRequest'
                            }
                        )
                except Exception as e:
                    print(f"[{region_name.upper()}] - error: {e}")
                    return None

            if response.status_code != 200:
                print(f"[{region_name.upper()}] - HTTP status: {response.status_code}")
                return None

            try:
                json_data = response.json()
            except json.JSONDecodeError as e:
                print(f"[{region_name.upper()}] - invalid JSON: {e}")
                print(f"Response preview: {response.text[:200]}")
                return None

            raw_dir = f"./cameroon/{region_name}/raw/{self.year}/{self.month}"
            os.makedirs(raw_dir, exist_ok=True)

            raw_filename = f"power_outages.CM.{region_name}.raw.{self.today}.json"
            raw_filepath = os.path.join(raw_dir, raw_filename)

            with open(raw_filepath, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            if isinstance(json_data, dict) and "data" in json_data:
                outage_count = len(json_data["data"])
            elif isinstance(json_data, list):
                outage_count = len(json_data)
            else:
                outage_count = 0

            print(f"[{region_name.upper()}] ✓ Saved raw data ({outage_count} outages)")

            return {
                'region': region_name,
                'filepath': raw_filepath,
                'outage_count': outage_count
            }

    async def scrape_all(self):
        tasks = [
            self.fetch_region(region_name, region_code)
            for region_name, region_code in self.regions.items()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful = 0
        failed = 0
        raw_files = []

        for region_name, result in zip(self.regions.keys(), results):
            if isinstance(result, Exception):
                print(f"[{region_name.upper()}] - exception: {result}")
                failed += 1
            elif result is None:
                failed += 1
            else:
                successful += 1
                raw_files.append(result)

        if raw_files:
            from utils.upload import Uploader
            uploader = Uploader("cameroon")

            for file_info in raw_files:
                region = file_info['region']
                filepath = file_info['filepath']
                filename = os.path.basename(filepath)
                s3_path = f"cameroon/{region}/raw/{self.year}/{self.month}/{filename}"
                try:
                    uploader.upload_file(filepath, s3_path)
                except Exception as e:
                    print(f"[{region.upper()}] - S3 upload failed: {e}")


        from post_process import ProcessCameroon
        processor = ProcessCameroon(today=self.today)
        output_file = processor.run()

        return output_file

    async def scrape_region(self, region_name):
        region_name = region_name.lower().replace('-', '_')

        if region_name not in self.regions:
            print(f"unknown region: {region_name}")
            return

        result = await self.fetch_region(region_name, self.regions[region_name])

        if result:
            print(f"raw data saved to {result['filepath']}")
            print(f" ({result['outage_count']} outages)")


def main():
    import sys

    scraper = CameroonScraper()

    if len(sys.argv) > 1:
        region = sys.argv[1]
        asyncio.run(scraper.scrape_region(region))
    else:
        asyncio.run(scraper.scrape_all())


if __name__ == "__main__":
    main()