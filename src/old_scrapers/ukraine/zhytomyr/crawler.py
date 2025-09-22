# Import necessary libraries
import datetime
from .utils import raw_file, mk_dir
import requests


# Name of the spider
name = "planned_disconnection_zhytomyr"
now = datetime.datetime.now()
one_day_later = now + datetime.timedelta(days=1)
formatted_start_date = str(int(now.timestamp()))
formatted_end_date = str(int(one_day_later.timestamp()))


def crawl_zhytomyr():
        url = "https://www.ztoe.com.ua/unhooking-search.php"

        for rem_id in ['1', '2', '3', '4', '5', '7', '9', '11', '13', '14', '17', '18', '19', '20', '21', '23', '25']:
            payload = {
                "rem_id": rem_id,
                "naspunkt_id": "0",
                "vulica_id": "0",
                "all": "%EF%EE%EA%E0%E7%E0%F2%E8 %F9%E5 1264 %E7%E0%EF%E8%F1%B3%E2"
            }

            response = requests.post(url, data=payload)

            current_html_file = raw_file.replace(".json", f".{rem_id}.html")
            with open(current_html_file, 'w') as f:
                f.write(response.text)


if __name__ == "__main__":
    mk_dir()
    crawl_zhytomyr()