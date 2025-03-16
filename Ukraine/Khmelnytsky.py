# Import necessary libraries
import datetime

import scrapy
from scrapy import cmdline


class PlannedDisconnectionSpider(scrapy.Spider):
    # Name of the spider
    name = "planned_disconnection_khmelnytsky"

    # Allowed domains for the spider
    allowed_domains = ["hoe.com.ua"]

    start_urls = ["https://hoe.com.ua/shutdown/all"]

    def start_requests(self):
        regions = [
            '4', '12', '17', '21', '23', '24',
        ]
        now = datetime.datetime.now()
        one_day_later = now + datetime.timedelta(days=1)
        formatted_start_date = now.strftime("%d.%m.%Y")
        formatted_end_date = one_day_later.strftime("%d.%m.%Y")
        for region in regions:
            yield scrapy.FormRequest(
                'https://hoe.com.ua/shutdown/eventlist',
                formdata={'TypeId': '2',
                          'PageNumber': '1',
                          'RemId': region,
                          'DateRange': f'{formatted_start_date} - {formatted_end_date}',
                          'X-Requested-With': 'XMLHttpRequest'},
                callback=self.parse
            )

    def parse(self, response):
        # Extract relevant data from the page
        # Adjust the selectors based on the structure of the webpage
        planned_disconnections = response.xpath('//tbody/tr[not(@class)]')
        date_format = "%d.%m.%Y %H:%M"
        # print("planned_disconnections", planned_disconnections)

        for disconnection in planned_disconnections:
            # print("disconnection", disconnection)
            planned_end_time = "".join(disconnection.xpath('.//td[5]/div//text()').getall())
            start_time = "".join(disconnection.xpath('.//td[4]/div//text()').getall())
            disconnection_type = disconnection.xpath('.//td[2]//text()').get("").strip()
            city_list = disconnection.xpath('.//p[@class="city"]/text()').get("").strip()
            # street_list = disconnection.xpath('.//td[@class="addresses"]/text()').get()
            # inform_time = disconnection.xpath('.//td[3]/text()').get("").strip()
            yield {
                'end':str(datetime.datetime.strptime(planned_end_time, date_format)),
                'start': str(datetime.datetime.strptime(start_time, date_format)),
                'duration_(hours)': "{:.2f}".format((datetime.datetime.strptime(planned_end_time, date_format) - datetime.datetime.strptime(start_time, date_format)).total_seconds() / 3600),
                'areas_affected': city_list,
                'disconnection_type': "Planned" if disconnection_type == "\u041f\u043b\u0430\u043d\u043e\u0432\u0456" else "Emergency",
            }



if __name__ == "__main__":
    cmdline.execute("scrapy runspider Khmelnytsky.py -O Khmelnytsky.json -s FEED_EXPORT_ENCODING=utf-8".split())