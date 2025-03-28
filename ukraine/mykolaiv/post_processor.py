import datetime
import json
from utils import processed_file, raw_file, mk_dir

def post_process_mykolaiv():
    file = open(raw_file, 'r')
    data = json.load(file)
    res = []
    with open(processed_file, 'w', encoding='utf-8') as f:
        for page in data:
            items = page['data']
            date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
            for item in items:
                start = datetime.datetime.strptime(item['start_at'], date_format)
                end = datetime.datetime.strptime(item['finish_at'], date_format)
                duration = (end - start).total_seconds() / 3600
                res.append({
                    "end": str(end),
                    "start": str(start),
                    "duration_(hours)": "{:.2f}".format(duration),
                    "event_type": item['type'],
                    "areas_affected": item['addr'],
                    "country": "ukraine"
                })


        json.dump(res, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    mk_dir()
    post_process_mykolaiv()