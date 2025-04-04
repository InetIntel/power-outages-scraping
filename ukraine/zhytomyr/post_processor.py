import datetime
import json
import os

import lxml.html
from utils import processed_file, mk_dir, raw_file

time_spans = ['00:00-00:30','00:30-01:00','01:00-01:30','01:30-02:00',
              '02:00-02:30','02:30-03:00','03:00-03:30','03:30-04:00',
              '04:00-04:30','04:30-05:00','05:00-05:30','05:30-06:00',
              '06:00-06:30','06:30-07:00','07:00-07:30','07:30-08:00',
              '08:00-08:30','08:30-09:00','09:00-09:30','09:30-10:00',
              '10:00-10:30','10:30-11:00', '11:00-11:30', '11:30-12:00',
              '12:00-12:30', '12:30-13:00', '13:00-13:30', '13:30-14:00',
              '14:00-14:30','14:30-15:00','15:00-15:30', '15:30-16:00',
              '16:00-16:30', '16:30-17:00','17:00-17:30','17:30-18:00',
              '18:00-18:30', '18:30-19:00', '19:00-19:30', '19:30-20:00',
              '20:00-20:30', '20:30-21:00', '21:00-21:30', '21:30-22:00',
              '22:00-22:30', '22:30-23:00', '23:00-23:30', '23:30-24:00']
def post_process_zhytomyr():
    with open(raw_file, 'r') as f:
        time_cells = lxml.html.fromstring(f.read()).xpath('//table[@cellspacing="0"]/tbody/tr/td')

        for id, time_cell in enumerate(time_cells):
            if time_cell.xpath("@background") == '#ff0000':
                link = time_cell.xpath("//a/@href")
                current_start_time = 0.5 * id
                current_end_time = current_start_time + 0.5

    res = []
    with open(processed_file, 'w', encoding='utf-8') as f:

        json.dump(res, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    mk_dir()
    post_process_zhytomyr()