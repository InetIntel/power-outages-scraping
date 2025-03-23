# Import necessary libraries
import datetime
import json

import httpx
import scrapy
from scrapy import cmdline


class PlannedDisconnectionSpider(scrapy.Spider):
    # Name of the spider
    name = "planned_disconnection_zhytomyr"
    now = datetime.datetime.now()
    one_day_later = now + datetime.timedelta(days=1)
    formatted_start_date = str(int(now.timestamp()))
    formatted_end_date = str(int(one_day_later.timestamp()))

    def start_requests(self):
        for rem_id in range(1, 3):
            body = {"rem_id": str(rem_id), "naspunkt_id": "0", "all":"1"}
            yield scrapy.FormRequest(
            method="POST",
            url='https://www.ztoe.com.ua/unhooking-search.php',
            formdata= body,
            callback=self.parse,
            meta={'rem_id': rem_id, 'naspunkt_id': 0}
            )

    def parse(self, response):
        outages = response.xpath("//table/tr")
        for outage in outages:
            rem = outage.xpath("./td[1]//text()").get("")
            locality = outage.xpath("./td[2]//text()").get("")
            street = outage.xpath("./td[3]//text()").get("")
            house = outage.xpath("./td[4]//text()").get("")
            turn = outage.xpath("./td[5]//text()").get("")
            yield {
                "rem": rem.strip(),
                "locality": locality.strip(),
                "street": street.strip(),
                "house": house.strip(),
                "turn": turn.strip()
            }
        naspunkt_ids = response.xpath('//select[@name="naspunkt_id"]/option')
        rem_id = response.meta.get('rem_id')
        current_naspunkt_id = response.meta.get('naspunkt_id')
        if current_naspunkt_id == 0:
            for naspunkt_id in naspunkt_ids:
                naspunkt_id = naspunkt_id.xpath('.//@value').get()
                print("naspunkt_id is", naspunkt_id)
                yield response.follow(url='https://www.ztoe.com.ua/unhooking-search.php', method='POST', body=f'{{"rem_id": {rem_id}, "naspunkt_id": {naspunkt_id}, "all":"1"}}',
                                      callback=self.parse, meta={'rem_id': rem_id, 'naspunkt_id': naspunkt_id})


if __name__ == "__main__":
    cmdline.execute("scrapy runspider Zhytomyr_raw.py -O Zhytomyr_raw.json".split())