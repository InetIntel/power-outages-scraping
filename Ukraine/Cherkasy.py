# Import necessary libraries
import json
import re

import scrapy
from scrapy import cmdline
from datetime import datetime
from dateutil.relativedelta import relativedelta


class PlannedDisconnectionSpider(scrapy.Spider):
    # Name of the spider
    name = "planned_disconnection_cherkasy"

    # Allowed domains for the spider
    allowed_domains = ["cherkasyoblenergo.com"]

    # Start URL for the spider
    now = datetime.now()
    start_date = now.strftime("%d.%m.%Y")
    end_date = (now + relativedelta(days=1)).strftime("%d.%m.%Y")

    disconnection_types = [0, 1, 2] # 0: Planned, 1: Emergency, 2: Outage Schedules
    dept_ids = [i+1 for i in range(22)]

    start_urls = []
    for disconnection_type in disconnection_types:
        for dept_id in dept_ids:
            start_urls.append(f"https://cabinet.cherkasyoblenergo.com/api_new/disconn.php?op=disconn_by_dept&"
                              f"disconn_selector={disconnection_type}&n_date={start_date}&k_date={end_date}&&dept_id={dept_id}")

    def parse(self, response):
        response_json = json.loads(response.body)
        # Define the date format
        date_format = "%d.%m.%Y %H:%M"
        if isinstance(response_json['DISCONNECTIONS'], list):
            print(response_json['DISCONNECTIONS'])
        else:
            for number, disconnection in response_json['DISCONNECTIONS'].items():
                start = disconnection['DATE_START']
                end = disconnection['DATE_STOP'].split("(")[0].strip()

                # Parse the date strings into datetime objects
                start_time = datetime.strptime(start, date_format)
                stop_time = datetime.strptime(end, date_format)
                duration = (stop_time - start_time).total_seconds() / 3600

                event_category = disconnection['DISCONN_TYPE']
                country = 'Ukraine'
                areas_affected = disconnection['ADDRESS']
                # Regular expression to find text between <br> tags
                matches = re.findall(r'<br>(.*?)<br>', areas_affected)

                cleaned_matches_areas = [match for match in matches]

                yield {
                    "start": str(start_time),
                    "end": str(stop_time),
                    "duration_(hours)": "{:.2f}".format(duration),
                    "event_category": "Planned" if event_category == '\u041f\u043b\u0430\u043d\u043e\u0432\u0435' else "Emergency",
                    "country": country,
                    "areas_affected": cleaned_matches_areas
                }




if __name__ == "__main__":
    cmdline.execute("scrapy runspider Cherkasy.py -O Cherkasy.json -s FEED_EXPORT_ENCODING=utf-8".split())