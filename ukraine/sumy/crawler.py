# Import necessary libraries
import json

import scrapy
from scrapy import cmdline

from utils import mk_dir, raw_file


class PlannedDisconnectionSpider(scrapy.Spider):
    # Name of the spider
    name = "planned_disconnection_sumy"

    download_delay = 5

    start_urls = [
        "https://www.soe.com.ua/includes/vidklyuchennya_srv_CURL.php?cmd=readAccidentsFutureByCity&c=5920610100",
        "https://www.soe.com.ua/includes/vidklyuchennya_srv_CURL.php?cmd=readAccidentsFutureByCity&c=5920910100",
        "https://www.soe.com.ua/includes/vidklyuchennya_srv_CURL.php?cmd=readAccidentsFutureByCity&c=5921255100",
        ]

    def parse(self, response):
        yield json.loads(response.body)

if __name__ == "__main__":
    mk_dir()
    cmdline.execute(f"scrapy runspider crawler.py -O {raw_file} -s FEED_EXPORT_ENCODING=utf-8".split())