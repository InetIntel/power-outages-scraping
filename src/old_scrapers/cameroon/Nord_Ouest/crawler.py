import json

import requests
from .utils import raw_file, mk_dir

def crawl_nord_ouest():
    mk_dir()
    response = requests.post("https://alert.eneo.cm/ajaxOutage.php", data={
        'region': '8'
    })

    with open(f'{raw_file}', 'w') as f:
        json.dump(response.json(), f)


