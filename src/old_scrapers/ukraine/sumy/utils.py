
import os
import sys
sys.path.append("../..")
from ukraine.constants import root_dir, current_date, current_year, current_month

current_dir = "ukraine/sumy"
raw_file = f'{root_dir}/power-outages-data/{current_dir}/raw/{current_year}/{current_month}/power_outages.UA.sumy.raw.{current_date}.json'
processed_file = raw_file.replace("raw", "processed")

def mk_dir():
    raw_dir = "/".join(raw_file.split('/')[:-1])
    processed_dir = "/".join(processed_file.split('/')[:-1])
    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir)
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)
