import requests
import json
from .utils import raw_file, mk_dir

def crawl_douala():
    mk_dir()
    response = requests.post("https://alert.eneo.cm/ajaxOutage.php", data={
        'region': 'X-22'
    })

    with open(f'{raw_file}', 'w') as f:
        json.dump(response.json(), f)


