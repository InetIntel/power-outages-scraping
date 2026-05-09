from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import json
import sys
from utils.upload import Uploader


class RikudenHTMLProcessor:
    def __init__(self):
        base = Path(__file__).resolve().parent
        self.raw_dir = base / "data" / "raw"
        self.out_dir = base / "data" / "processed"
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def _latest_html(self):
        files = sorted(self.raw_dir.glob("rikuden_*.html"))
        if not files:
            raise RuntimeError("No rikuden_*.html files found in raw/")
        return files[-1]

    def _parse_table(self, html_bytes):
        soup = BeautifulSoup(html_bytes, "html.parser")

        table = soup.find("table", class_="mapc-cyo")
        if not table:
            raise RuntimeError("Could not find table.mapc-cyo")

        rows = table.find_all("tr")

        entries = []

        for tr in rows:
            cols = tr.find_all("td")
            if len(cols) != 7:
                continue  # Skip header row

            def clean(el):
                return " ".join(el.get_text(" ", strip=True).split())

            start = clean(cols[0])
            end = clean(cols[1])
            prefecture = clean(cols[2])
            city = clean(cols[3])

            # Towns: handle <BR> lines
            towns = cols[4].get_text(" ", strip=True)
            towns = " ".join(towns.split())
            towns = towns.replace(" ,", ",").replace(", ", ", ")
            towns = towns.replace(" , ", ", ")

            households_raw = clean(cols[5])
            reason_raw = clean(cols[6])

            # Normalize
            households = (
                None
                if households_raw
                in ("（自動復旧等）", "(自動復旧等)", "(Automatic recovery)")
                else households_raw
            )
            reason = None if reason_raw in ("―", "-", "") else reason_raw

            entries.append(
                {
                    "start_time": start,
                    "end_time": end,
                    "prefecture": prefecture,
                    "city": city,
                    "towns": towns,
                    "households": households,
                    "reason": reason,
                }
            )

        return entries

    def run(self):
        uploader = Uploader("japan")
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")

        prefix = f"japan/hokuriku/raw/{year}/{month}/"
        listing = uploader.client.list_objects_v2(Bucket="japan", Prefix=prefix)
        for obj in listing.get("Contents", []):
            key = obj["Key"]
            local_path = self.raw_dir / Path(key).name
            uploader.download_file(key, str(local_path))

        html_path = self._latest_html()
        print(f"Parsing -> {html_path}")

        html_bytes = html_path.read_bytes()
        entries = self._parse_table(html_bytes)

        result = {
            "provider": "rikuden",
            "country": "japan",
            "fetched_at": datetime.utcnow().isoformat(),
            "entries": entries,
        }

        out_file = (
            self.out_dir
            / f"rikuden_processed_{datetime.now().strftime('%Y%m%dT%H%M%S')}.json"
        )
        out_file.write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        print(f"Saved -> {out_file}")

        # Upload processed file to shared volume
        s3_processed = f"japan/hokuriku/processed/{year}/{month}/{out_file.name}"
        uploader.upload_file(str(out_file), s3_processed)


if __name__ == "__main__":
    RikudenHTMLProcessor().run()
