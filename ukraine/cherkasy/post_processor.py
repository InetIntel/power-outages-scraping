import json
import os
import re
from datetime import datetime

from utils import raw_file, processed_file


def post_process_cherkasy():
    file = open(raw_file, 'r')
    data = json.load(file)
        # Define the date format
    date_format = "%d.%m.%Y %H:%M"
    res = []
    with open(processed_file, 'w', encoding='utf-8') as f:
        for disconnection_item in data:
            if isinstance(disconnection_item['DISCONNECTIONS'], list):
                print(disconnection_item['DISCONNECTIONS'])
            else:
                for number, disconnection in disconnection_item['DISCONNECTIONS'].items():
                    start = disconnection['DATE_START']
                    end = disconnection['DATE_STOP'].split("(")[0].strip()

                    # Parse the date strings into datetime objects
                    start_time = datetime.strptime(start, date_format)
                    stop_time = datetime.strptime(end, date_format)
                    duration = (stop_time - start_time).total_seconds() / 3600

                    event_category = disconnection['DISCONN_TYPE']
                    country = 'ukraine'
                    areas_affected = disconnection['ADDRESS']
                    # Regular expression to find text between <br> tags
                    matches = re.findall(r'<br>(.*?)<br>', areas_affected)

                    cleaned_matches_areas = [match for match in matches]

                    line = {
                        "start": str(start_time),
                        "end": str(stop_time),
                        "duration_(hours)": "{:.2f}".format(duration),
                        "event_category": "Planned" if event_category == '\u041f\u043b\u0430\u043d\u043e\u0432\u0435' else "Emergency",
                        "country": country,
                        "areas_affected": cleaned_matches_areas
                    }

                    res.append(line)
        json.dump(res, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    post_process_cherkasy()