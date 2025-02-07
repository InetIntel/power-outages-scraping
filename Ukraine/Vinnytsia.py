# Import necessary libraries
import scrapy
from scrapy import cmdline


class PlannedDisconnectionSpider(scrapy.Spider):
    # Name of the spider
    name = "planned_disconnection_vinnystia"

    # Allowed domains for the spider
    allowed_domains = ["voe.com.ua"]

    # Start URL for the spider
    years = ['2023', '2024', '2025']
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    regions = ['23', '25', '26', '27', '29', '30', '31', '32', '33' ,'35', '36', '37', '38', '39'
               ,'41', '42', '43', '45', '46', '47', '48', '50', '51', '52', '53', '55', '56', '57']

    start_urls = []

    for year in years:
        for month in months:
            for region in regions:
                start_urls.append(f"https://voe.com.ua/disconnection/planned/{year}/{month}/{region}")

    def parse(self, response):
        # Extract relevant data from the page
        # Adjust the selectors based on the structure of the webpage
        planned_disconnections = response.xpath('//table')

        for disconnection in planned_disconnections:
            yield {
                'region': disconnection.xpath('.//h2/text()').get(),
                'description': disconnection.xpath('.//p/text()').get(),
                'date': disconnection.xpath('.//span[@class="date"]/text()').get(),
                'location': disconnection.xpath('.//span[@class="location"]/text()').get(),
            }

        # If there are pagination links, follow them
        next_page = response.xpath('//a[@class="next-page"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)


if __name__ == "__main__":
    cmdline.execute("scrapy runspider Vinnytsia.py".split())