import requests
from pathlib import Path
from datetime import datetime, timedelta

class KyushuScraper:
    def __init__(self):
        self.base_path = Path(__file__).resolve().parent / "data" / "raw"
        self.base_path.mkdir(parents=True, exist_ok=True)

    def fetch_for_date(self, date_str):
        base_url = "https://www.kyuden.co.jp/td_teiden/csv/RES{}_{}.csv"
        found_any = False

        for res_id in range(40, 47):
            url = base_url.format(res_id, date_str)

            try:
                resp = requests.get(url, timeout=5)

                if resp.status_code == 200 and resp.content:
                    save_path = self.base_path / f"RES{res_id}_{date_str}.csv"
                    with open(save_path, "wb") as f:
                        f.write(resp.content)

                    print(f"Saved: RES{res_id} for {date_str}")
                    found_any = True

            except Exception as e:
                print(f"Error fetching RES{res_id}_{date_str}: {e}")

        if not found_any:
            print(f"No CSV found for {date_str}")

    def fetch_last_7_days(self):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        current = start_date
        while current <= end_date:
            date_str = current.strftime("%Y%m%d")
            date_format = datetime.strptime(date_str, "%Y%m%d").strftime("%m/%d/%Y") 
            print(f"\n=== Fetching {date_format} ===")

            self.fetch_for_date(date_str)
            current += timedelta(days=1)


if __name__ == "__main__":
    scraper = KyushuScraper()
    scraper.fetch_last_7_days()
