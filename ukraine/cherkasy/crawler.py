# Import necessary libraries
import json
import os

import scrapy
from scrapy import cmdline
from datetime import datetime
from dateutil.relativedelta import relativedelta

from ukraine.utils import current_year, current_month, current_date

current_dir = "/".join(os.getcwd().split("/")[-2:])
save_file = f'./power_outage_data/{current_dir}/raw/{current_year}/{current_month}/power_outages.UA.cherkasky.raw.{current_date}.json'


class PlannedDisconnectionSpider(scrapy.Spider):
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

    start_urls = []
    for disconnection_type in disconnection_types:
        for dept_id in dept_ids:
            start_urls.append(f"https://cabinet.cherkasyoblenergo.com/api_new/disconn.php?op=disconn_by_dept&"
                              f"disconn_selector={disconnection_type}&n_date={start_date}&k_date={end_date}&&dept_id={dept_id}")

    def parse(self, response):
        yield json.loads(response.body)

if __name__ == "__main__":
    cmdline.execute(f"scrapy runspider crawler.py -O {save_file}  -s FEED_EXPORT_ENCODING=utf-8".split())