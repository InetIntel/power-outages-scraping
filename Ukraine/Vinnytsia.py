# Import necessary libraries
import scrapy
from scrapy import cmdline


class PlannedDisconnectionSpider(scrapy.Spider):
    # Name of the spider
    name = "planned_disconnection_vinnystia"

    # Allowed domains for the spider
    allowed_domains = ["voe.com.ua"]

    # Start URL for the spider
    years = ['2022', '2023', '2024', '2025']
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    regions = ['23', '25', '26', '27', '29', '30', '31', '32', '33', '35', '36', '37', '38', '39'
        , '41', '42', '43', '45', '46', '47', '48', '50', '51', '52', '53', '55', '56', '57']
    types = ['planned', 'emergency']

    start_urls = []

    for year in years:
        for month in months:
            for region in regions:
                for type in types:
                    start_urls.append(f"https://voe.com.ua/disconnection/{type}/{year}/{month}/{region}")

    def parse(self, response):
        # Extract relevant data from the page
        # Adjust the selectors based on the structure of the webpage
        planned_disconnections = response.xpath('//tr[@class="row"]')

        for disconnection in planned_disconnections:
            planned_end_time = disconnection.xpath('.//td[@class="accend_plan"]/text()').get()
            actual_end_time = disconnection.xpath('.//td[@class="accend_fact"]/text()').get()
            start_time = disconnection.xpath('.//td[@class="accbegin"]/text()').get()
            disconnection_type = disconnection.xpath('.//td[@class="acctype"]/text()').get()
            city_list = disconnection.xpath('.//td[@class="city_list"]/text()').get()
            street_list = disconnection.xpath('.//td[@class="addresses"]/text()').get()
            status = disconnection.xpath('.//td[@class="status"]/text()').get()
            inform_time = disconnection.xpath('.//td[@class="dtupdate"]/text()').get()
            yield {
                'planned_end_time': planned_end_time,
                'actual_end_time': actual_end_time,
                'start_time': start_time,
                'city_list': city_list,
                'street_list': street_list,
                'disconnection_type': disconnection_type,
                'status': status,
                'inform_time': inform_time
            }

        # If there are pagination links, follow them
        next_page = response.xpath('//a[@rel="next-page"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)


if __name__ == "__main__":
    cmdline.execute("scrapy runspider Vinnytsia.py -O Vinnytsia.json".split())