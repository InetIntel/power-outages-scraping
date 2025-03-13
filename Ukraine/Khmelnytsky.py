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
        five_days_later = now + datetime.timedelta(days=1)
        formatted_start_date = now.strftime("%d.%m.%Y")
        formatted_end_date = five_days_later.strftime("%d.%m.%Y")
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
        # print("planned_disconnections", planned_disconnections)

        for disconnection in planned_disconnections:
            # print("disconnection", disconnection)
            planned_end_time = "".join(disconnection.xpath('.//td[5]/div//text()').getall())
            start_time = "".join(disconnection.xpath('.//td[4]/div//text()').getall())
            disconnection_type = disconnection.xpath('.//td[2]//text()').get("").strip()
            city_list = disconnection.xpath('.//p[@class="city"]/text()').get("").strip()
            # street_list = disconnection.xpath('.//td[@class="addresses"]/text()').get()
            inform_time = disconnection.xpath('.//td[3]/text()').get("").strip()
            yield {
                'planned_end_time': planned_end_time,
                'start_time': start_time,
                'city_list': city_list,
                'disconnection_type': disconnection_type,
                'inform_time': inform_time
            }



if __name__ == "__main__":
    cmdline.execute("scrapy runspider Khmelnytsky.py -O Khmelnytsky.json".split())