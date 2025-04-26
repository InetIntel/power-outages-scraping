# Import necessary libraries
import json
import scrapy
from ukraine.sumy.utils import raw_file


class SumySpider(scrapy.Spider):
    # Name of the spider
    name = "planned_disconnection_sumy"
    custom_settings = {
            "FEEDS": {
            f"{raw_file}": {"format": "json", "overwrite": True},
        },
        "FEED_EXPORT_ENCODING": "utf-8"
        }

    download_delay = 5

    # This is the partial list of cities since the website requires manual input of city name
    start_urls = [
        "https://www.soe.com.ua/includes/vidklyuchennya_srv_CURL.php?cmd=readAccidentsFutureByCity&c=5920610100",
        "https://www.soe.com.ua/includes/vidklyuchennya_srv_CURL.php?cmd=readAccidentsFutureByCity&c=5920910100",
        "https://www.soe.com.ua/includes/vidklyuchennya_srv_CURL.php?cmd=readAccidentsFutureByCity&c=5921255100",
        ]

    def parse(self, response):
        yield json.loads(response.body)