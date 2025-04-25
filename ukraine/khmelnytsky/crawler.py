# Import necessary libraries
import datetime
import scrapy
from scrapy import cmdline

from .utils import raw_dir, mk_dir
from ukraine.constants import current_date


class KhmelnytskySpider(scrapy.Spider):
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
                callback=self.parse,
                meta={"region": region}
            )

    def parse(self, response):
        # Extract relevant data from the page
        # Adjust the selectors based on the structure of the webpage
        with open(f"{raw_dir}/power_outages.UA.khmelnytsky.raw.{current_date}.{response.meta.get('region')}.html", 'w') as f:
            f.write(response.text)

if __name__ == "__main__":
    mk_dir()
    cmdline.execute(f"scrapy runspider crawler.py -s FEED_EXPORT_ENCODING=utf-8".split())