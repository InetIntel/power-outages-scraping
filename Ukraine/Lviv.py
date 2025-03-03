# Import necessary libraries
import json

import scrapy
from scrapy import cmdline
from datetime import datetime

class PlannedDisconnectionSpider(scrapy.Spider):
    # Name of the spider
    name = "planned_disconnection_cherkasy"

    # Start URL for the spider
    now = datetime.now()

    def start_requests(self):
        url = "https://power-api.loe.lviv.ua/api/pw_accidents?page=1" # don't need to change the page, it will fetch all the pages
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'if-none-match': 'W/"b4bb6b850029e95544f57e4cd3fafe9d"',
            'origin': 'https://poweron.loe.lviv.ua',
            'referer': 'https://poweron.loe.lviv.ua/',
        }
        yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response):
        yield json.loads(response.body)


if __name__ == "__main__":
    cmdline.execute("scrapy runspider Lviv.py -O Lviv.json".split())