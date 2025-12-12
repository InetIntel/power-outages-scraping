import os
import asyncio
import httpx
from datetime import datetime
from bs4 import BeautifulSoup


class MEA_Thailand:
    def __init__(self, concurrent_connections=3):
        self.base_url = (
            "https://www.mea.or.th/en/public-relations/power-outage-notifications/news"
        )
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.folder_path = None
        self.year = str(datetime.now().year)
        self.month = str(datetime.now().month).zfill(2)
        self.concurrent_connections = concurrent_connections
        self.semaphore = asyncio.Semaphore(concurrent_connections)

    def check_folder(self, type):
        self.folder_path = "./thailand/mea/" + type + "/" + self.year + "/" + self.month
        os.makedirs(self.folder_path, exist_ok=True)

    async def fetch_listing_page(self, session, page=1):
        """Fetch the listing page to get announcement URLs"""
        url = f"{self.base_url}?page={page}" if page > 1 else self.base_url

        async with self.semaphore:
            try:
                response = await session.get(url)
                if response.status_code == 200:
                    return {
                        "page": page,
                        "html_content": response.text,
                        "status": "success",
                    }
                else:
                    return {
                        "page": page,
                        "html_content": None,
                        "status": "error",
                        "error": f"HTTP {response.status_code}",
                    }
            except Exception as e:
                return {
                    "page": page,
                    "html_content": None,
                    "status": "error",
                    "error": str(e),
                }

    async def fetch_announcement(self, session, url, announcement_id):
        """Fetch individual announcement page"""
        full_url = f"https://www.mea.or.th{url}"

        async with self.semaphore:
            try:
                response = await session.get(full_url)
                if response.status_code == 200:
                    return {
                        "announcement_id": announcement_id,
                        "url": url,
                        "html_content": response.text,
                        "status": "success",
                    }
                else:
                    return {
                        "announcement_id": announcement_id,
                        "url": url,
                        "html_content": None,
                        "status": "error",
                        "error": f"HTTP {response.status_code}",
                    }
            except Exception as e:
                return {
                    "announcement_id": announcement_id,
                    "url": url,
                    "html_content": None,
                    "status": "error",
                    "error": str(e),
                }

    def extract_announcement_urls(self, html_content):
        """Extract announcement URLs from listing page"""
        soup = BeautifulSoup(html_content, "html.parser")
        urls = []

        # Find all announcement cards
        cards = soup.find_all("div", class_="card-item")

        for card in cards:
            link = card.find("a")
            if link and link.get("href"):
                href = link.get("href")
                title = link.get("title", "")
                # Extract announcement ID from URL
                announcement_id = href.split("/")[-1]
                urls.append({"url": href, "id": announcement_id, "title": title})

        return urls

    async def fetch_all(self):
        from utils.upload import Uploader

        self.check_folder("raw")

        all_urls = []
        seen_ids = set()
        page = 1

        async with httpx.AsyncClient(timeout=60.0) as client:
            while True:
                result = await self.fetch_listing_page(client, page)

                if result.get("status") != "success":
                    break

                urls = self.extract_announcement_urls(result.get("html_content"))

                if not urls:
                    break

                # Detect duplicates
                new_items_found = False
                for item in urls:
                    if item["id"] not in seen_ids:
                        seen_ids.add(item["id"])
                        all_urls.append(item)
                        new_items_found = True

                if not new_items_found:
                    break

                page += 1

            announcement_tasks = []
            for url_data in all_urls:
                task = self.fetch_announcement(client, url_data["url"], url_data["id"])
                announcement_tasks.append(task)

            announcement_results = await asyncio.gather(*announcement_tasks)

            # Filter successful results
            all_data = [
                result
                for result in announcement_results
                if result.get("status") == "success"
            ]

        if all_data:
            # Save individual HTML files locally
            for item in all_data:
                announcement_id = item.get("announcement_id")
                html_content = item.get("html_content")

                if html_content:
                    html_file_name = (
                        f"power_outages.TH.mea.raw.{self.today}.{announcement_id}.html"
                    )
                    html_file_path = os.path.join(self.folder_path, html_file_name)

                    with open(html_file_path, "w", encoding="utf-8") as file:
                        file.write(html_content)

            # Upload to S3
            try:
                uploader = Uploader("thailand")

                for item in all_data:
                    announcement_id = item.get("announcement_id")
                    if item.get("html_content"):
                        html_file_name = f"power_outages.TH.mea.raw.{self.today}.{announcement_id}.html"
                        html_file_path = os.path.join(self.folder_path, html_file_name)
                        html_s3_path = f"thailand/mea/raw/{self.year}/{self.month}/{html_file_name}"
                        uploader.upload_file(html_file_path, html_s3_path)

            except Exception as e:
                pass

    async def scrape(self):
        await self.fetch_all()


if __name__ == "__main__":
    mea = MEA_Thailand()
    asyncio.run(mea.scrape())
