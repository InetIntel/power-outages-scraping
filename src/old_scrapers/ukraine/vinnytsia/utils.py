import os
from ukraine.constants import root_dir, current_date, current_year, current_month

current_dir = "ukraine/vinnytsia"
raw_dir = f'{root_dir}/power-outages-data/{current_dir}/raw/{current_year}/{current_month}'
processed_file = raw_dir.replace("raw", "processed") + f'/power_outages.UA.vinnytsia.processed.{current_month}.json'

def mk_dir():
    split_raw_dir = "/".join(raw_dir.split('/'))
    processed_dir = "/".join(processed_file.split('/')[:-1])
    if not os.path.exists(split_raw_dir):
        os.makedirs(split_raw_dir)
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)
