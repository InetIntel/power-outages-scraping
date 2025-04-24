import datetime
import json
import os

import lxml.html
from .utils import processed_file, raw_dir, mk_dir

def post_process_vinnytsia():
    files = os.listdir(raw_dir)
    res = []
    with open(processed_file, 'w', encoding='utf-8') as f1:
        for file in files:
            with open(os.path.join(raw_dir, file), 'r') as f2:
                content = f2.read()
                planned_disconnections = lxml.html.fromstring(content).xpath('//tr[@class="row"]')
                date_format = "%Y-%m-%d %H:%M:%S"
                for disconnection in planned_disconnections:
                    planned_end_time = (disconnection.xpath('.//td[@class="accend_plan"]/text()') or [''])[0]
                    actual_end_time = (disconnection.xpath('.//td[@class="accend_fact"]/text()') or [''])[0]
                    start_time = (disconnection.xpath('.//td[@class="accbegin"]/text()') or [''])[0]
                    disconnection_type = (disconnection.xpath('.//td[@class="acctype"]/text()') or [''])[0]
                    village_list = [{"type":"city", "area":area} for area in (disconnection.xpath('.//td[@class="city_list"]/text()') or [''])[0].split(",")]
                    # street_list = disconnection.xpath('.//td[@class="addresses"]/text()').get()
                    # status = disconnection.xpath('.//td[@class="status"]/text()').get()
                    # inform_time = disconnection.xpath('.//td[@class="dtupdate"]/text()').get()
                    end_time_string = planned_end_time
                    if actual_end_time:
                        end_time_string = actual_end_time

                    if end_time_string:
                        end_time = datetime.datetime.strptime(end_time_string ,date_format)
                    else:
                        end_time = "unknown"
                    start_time = datetime.datetime.strptime(start_time, date_format)
                    duration = '{:.2f}'.format((end_time - start_time).total_seconds() / 3600) if isinstance(end_time, datetime.datetime) and isinstance(start_time, datetime.datetime) else 'unknown'
                    res.append({
                        'end': str(end_time),
                        'start': str(start_time),
                        'duration': duration,
                        'areas_affected': village_list,
                        'event_category': "Planned" if disconnection_type == '\u041f\u043b\u0430\u043d\u043e\u0432\u0435 \u0432\u0456\u0434\u043a\u043b\u044e\u0447\u0435\u043d\u043d\u044f' else 'Emergency',
                    })

        json.dump(res, f1, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    mk_dir()
    post_process_vinnytsia()