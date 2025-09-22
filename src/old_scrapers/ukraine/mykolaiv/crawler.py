# Import necessary libraries
import datetime
import json
import scrapy
from ukraine.mykolaiv.utils import raw_file


class MykolaivSpider(scrapy.Spider):
    # Name of the spider
    name = "planned_disconnection_mykolaiv"
    now = datetime.datetime.now()
    one_day_later = now + datetime.timedelta(days=1)
    formatted_start_date = str(int(now.timestamp()))
    formatted_end_date = str(int(one_day_later.timestamp()))

    custom_settings = {
            "FEEDS": {
            f"{raw_file}": {"format": "json", "overwrite": True},
        },
        "FEED_EXPORT_ENCODING": "utf-8"
        }

    def start_requests(self):
        body = f'{{"page":1,"perPage":100,"from":{self.formatted_start_date},"to":{self.formatted_end_date} }}'
        yield scrapy.Request(
            method="POST",
            url='https://www.energy.mk.ua/outage/api/v1/outage',
            body= body,
            headers={
                'Referer': 'https://www.energy.mk.ua/vidklyuchennya/',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json',
            },
        callback=self.parse
        )

    def parse(self, response):
        response_body = json.loads(response.body)
        yield response_body

        if "next_page_url" in response_body:
            next_page_url = response_body["next_page_url"]
            if next_page_url:
                next_page = int(next_page_url.split("=")[1])
                yield response.follow(url='https://www.energy.mk.ua/outage/api/v1/outage',
                                      method="POST",
                                      body=f'{{"page":{next_page},"perPage":{100},"from": {self.formatted_start_date},"to": {self.formatted_end_date}}}',
                                      headers={
                                          'Referer': 'https://www.energy.mk.ua/vidklyuchennya/',
                                          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
                                          'Accept': 'application/json, text/plain, */*',
                                          'Content-Type': 'application/json',
                                      },
                              callback=self.parse
                            )