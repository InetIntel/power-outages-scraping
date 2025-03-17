# Import necessary libraries
import datetime

import scrapy
from scrapy import cmdline


class PlannedDisconnectionSpider(scrapy.Spider):
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
        # Extract relevant data from the page
        # Adjust the selectors based on the structure of the webpage
        planned_disconnections = response.xpath('//tr[@class="row"]')
        date_format = "%Y-%m-%d %H:%M:%S"
        for disconnection in planned_disconnections:
            planned_end_time = disconnection.xpath('.//td[@class="accend_plan"]/text()').get()
            actual_end_time = disconnection.xpath('.//td[@class="accend_fact"]/text()').get()
            start_time = disconnection.xpath('.//td[@class="accbegin"]/text()').get()
            disconnection_type = disconnection.xpath('.//td[@class="acctype"]/text()').get()
            city_list = disconnection.xpath('.//td[@class="city_list"]/text()').get()
            # street_list = disconnection.xpath('.//td[@class="addresses"]/text()').get()
            # status = disconnection.xpath('.//td[@class="status"]/text()').get()
            # inform_time = disconnection.xpath('.//td[@class="dtupdate"]/text()').get()
            end_time_string = planned_end_time
            if actual_end_time:
                end_time_string = actual_end_time

            if end_time_string is not None:
                end_time = datetime.datetime.strptime(end_time_string ,date_format)
            else:
                end_time = "unknown"
            start_time = datetime.datetime.strptime(start_time, date_format)
            duration = '{:.2f}'.format((end_time - start_time).total_seconds() / 3600) if isinstance(end_time, datetime.datetime) and isinstance(start_time, datetime.datetime) else 'unknown'
            yield {
                'end': str(end_time),
                'start': str(start_time),
                'duration': duration,
                'areas_affected': city_list,
                'event_category': "Planned" if disconnection_type == '\u041f\u043b\u0430\u043d\u043e\u0432\u0435 \u0432\u0456\u0434\u043a\u043b\u044e\u0447\u0435\u043d\u043d\u044f' else 'Emergency',
            }

        # If there are pagination links, follow them
        next_page = response.xpath('//a[@rel="next-page"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)


if __name__ == "__main__":
    cmdline.execute("scrapy runspider Vinnytsia.py -O Vinnytsia.json -s FEED_EXPORT_ENCODING=utf-8".split())