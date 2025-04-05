import datetime
import json
from utils import processed_file, raw_file, mk_dir

def post_process_sumy():
    file = open(raw_file, 'r')
    data_items = json.load(file)
    res = []
    with open(processed_file, 'w', encoding='utf-8') as f:
        for disconnections in data_items:
            disconnections = disconnections['list']
            date_format = "%Y-%m-%dT%H:%M:%S"
            for disconnection in disconnections:
                planned_end_time = datetime.datetime.strptime(disconnection[4], date_format)
                start_time = datetime.datetime.strptime(disconnection[3], date_format)
                duration = '{:.2f}'.format((planned_end_time - start_time).total_seconds() / 3600)
                res.append({
                    'end': str(planned_end_time),
                    'start': str(start_time),
                    'duration_(hours)': duration,
                    'areas_affected': disconnection[1],
                    'event_category': "Planned",
                })

        json.dump(res, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    mk_dir()
    post_process_sumy()