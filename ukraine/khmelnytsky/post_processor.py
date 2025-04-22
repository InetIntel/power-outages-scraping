import datetime
import json
import os

import lxml.html
from utils import processed_file, raw_file, mk_dir

def post_process_khmelnytsky():
    files = os.listdir(raw_file)
    date_format = "%d.%m.%Y %H:%M"
    res = []
    with open(processed_file, 'w', encoding='utf-8') as f1:
        for file in files:
            with open(os.path.join(raw_file, file), 'r') as f2:
                html_page = lxml.html.fromstring(f2.read())
                planned_disconnections = html_page.xpath('//tbody/tr[not(@class)]')
                for disconnection in planned_disconnections:
                    planned_end_time = "".join(disconnection.xpath('.//td[5]/div//text()'))
                    start_time = "".join(disconnection.xpath('.//td[4]/div//text()'))
                    disconnection_type = disconnection.xpath('.//td[2]//text()')[0].strip()
                    city_list = disconnection.xpath('.//p[@class="city"]/text()')
                    res.append({
                        'end':str(datetime.datetime.strptime(planned_end_time, date_format)),
                        'start': str(datetime.datetime.strptime(start_time, date_format)),
                        'duration_(hours)': "{:.2f}".format((datetime.datetime.strptime(planned_end_time, date_format) - datetime.datetime.strptime(start_time, date_format)).total_seconds() / 3600),
                        'areas_affected': city_list,
                        'disconnection_type': "Planned" if disconnection_type == "\u041f\u043b\u0430\u043d\u043e\u0432\u0456" else "Emergency",
                    })

        json.dump(res, f1, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    mk_dir()
    post_process_khmelnytsky()