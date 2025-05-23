# Import necessary libraries
import datetime

import scrapy
from scrapy import cmdline
from .utils import mk_dir, raw_dir
from ukraine.constants import current_date


class VinnytsiaSpider(scrapy.Spider):
    # Name of the spider
    name = "planned_disconnection_vinnystia"

    # Allowed domains for the spider
    allowed_domains = ["voe.com.ua"]

    # Start URL for the spider
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    regions = ['23', '25', '26', '27', '29', '30', '31', '32', '33', '35', '36', '37', '38', '39'
        , '41', '42', '43', '45', '46', '47', '48', '50', '51', '52', '53', '55', '56', '57']
    types = ['planned', 'emergency']

    start_urls = []

    for region in regions:
        for type in types:
            start_urls.append(f"https://voe.com.ua/disconnection/{type}/{year}/{month}/{region}")

    def parse(self, response):
        region = response.url.split("/")[-1]
        type = response.url.split("/")[-4]
        with open(f"{raw_dir}/power_outages.UA.vinnytsia.raw.{current_date}.{region}.{type}.html", 'w') as f:
            f.write(response.text)

        # If there are pagination links, follow them
        next_page = response.xpath('//a[@rel="next-page"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)


if __name__ == "__main__":
    mk_dir()
    cmdline.execute(f"scrapy runspider crawler.py -s FEED_EXPORT_ENCODING=utf-8".split())