# Import necessary libraries
import json
import os

import scrapy
from scrapy import cmdline
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .utils import raw_file, mk_dir



class CherkasySpider(scrapy.Spider):
    # Name of the spider
    name = "planned_disconnection_cherkasy"

    # Allowed domains for the spider
    allowed_domains = ["cherkasyoblenergo.com"]

    # Start URL for the spider
    now = datetime.now()
    start_date = now.strftime("%d.%m.%Y")
    end_date = (now + relativedelta(days=1)).strftime("%d.%m.%Y")

    disconnection_types = [0, 1, 2] # 0: Planned, 1: Emergency, 2: Outage Schedules
    dept_ids = [i+1 for i in range(22)]

    custom_settings = {
            "FEEDS": {
            f"{raw_file}": {"format": "json", "overwrite": True},
        },
        "FEED_EXPORT_ENCODING": "utf-8"
        }

    start_urls = []
    for disconnection_type in disconnection_types:
        for dept_id in dept_ids:
            start_urls.append(f"https://cabinet.cherkasyoblenergo.com/api_new/disconn.php?op=disconn_by_dept&"
                              f"disconn_selector={disconnection_type}&n_date={start_date}&k_date={end_date}&&dept_id={dept_id}")

    def parse(self, response):
        yield json.loads(response.body)

if __name__ == "__main__":
    mk_dir()
    cmdline.execute(f"scrapy runspider crawler.py -O {raw_file}  -s FEED_EXPORT_ENCODING=utf-8".split())