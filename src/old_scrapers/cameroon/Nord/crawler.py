import json

import requests
from .utils import raw_file, mk_dir

def crawl_nord():
    mk_dir()
    response = requests.post("https://alert.eneo.cm/ajaxOutage.php", data={
        'region': '7'
    })

    with open(f'{raw_file}', 'w') as f:
        json.dump(response.json(), f)


