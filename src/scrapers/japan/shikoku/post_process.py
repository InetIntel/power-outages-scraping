import os
import json
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
from pathlib import Path
import re

class ShikokuProcessor:
    def __init__(self):
        self.provider = "shikoku"
        self.country_code = "JP"
        self.JST = timezone(timedelta(hours=9))
        self.today_iso = datetime.now(self.JST).strftime("%Y-%m-%d")

        self.base_dir = Path(__file__).resolve().parent
        self.raw_dir = self.base_dir / "data" / "raw"
        self.processed_dir = self.base_dir / "data" / "processed"
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def _to_iso(self, jp_datetime: str) -> str:
        """Convert '2025年12月8日 6時22分' → '2025-12-08 06:22'"""
        jp_datetime = jp_datetime.strip()
        if not jp_datetime:
            return ""
        match = re.match(r"(\d+)年(\d+)月(\d+)日\s+(\d+)時(\d+)分", jp_datetime)
        if not match:
            return jp_datetime
        year, month, day, hour, minute = map(int, match.groups())
        dt = datetime(year, month, day, hour, minute, tzinfo=self.JST)
        return dt.strftime("%Y-%m-%d %H:%M")

    def _clean_text(self, text: str) -> str:
        """Remove newlines, tabs, and extra spaces"""
        text = text.replace("\n", " ").replace("\t", " ")
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _parse_html(self, html_text: str) -> list:
        soup = BeautifulSoup(html_text, "html.parser")
        outages = []

        for div in soup.select("div.teiden_cont.detail"):
            try:
                h3 = div.find("h3")
                occurrence_raw = h3.find("em", string="発生日時").next_sibling.strip()
                recovery_raw = h3.find("em", string="復旧日時").next_sibling.strip()
                occurrence = self._to_iso(occurrence_raw)
                recovery = self._to_iso(recovery_raw)

                households_tag = h3.find("span", class_="kosuu")
                households = households_tag.i.get_text(strip=True) if households_tag else ""

                reason_tag = div.find("dl", class_="flex")
                reason = reason_tag.find("dd").get_text(strip=True) if reason_tag else ""

                areas = []
                table = div.find("table")
                if table:
                    for tr in table.find_all("tr"):
                        prefecture = tr.find("th").get_text(strip=True) if tr.find("th") else ""
                        city_td = tr.find("td", class_="city")
                        city = city_td.get_text(strip=True) if city_td else ""
                        town_td = tr.find("td", class_="town")
                        area_text = self._clean_text(town_td.get_text(" ", strip=True)) if town_td else ""

                        # Skip empty or placeholder entries
                        if all([x in ["", "―"] for x in [prefecture, city, area_text]]):
                            continue

                        areas.append({
                            "prefecture": prefecture,
                            "city": city,
                            "area": area_text
                        })

                outages.append({
                    "occurrence_datetime": occurrence,
                    "recovery_datetime": recovery,
                    "reason": reason,
                    "households_affected": households,
                    "areas": areas
                })

            except Exception as e:
                print(f"[WARN] Failed to parse outage: {e}")
                continue

        return outages

    def run(self):
        all_outages = []

        for file in sorted(self.raw_dir.glob("*.html")):
            print(f"[PROCESS] Parsing {file.name}")
            html = file.read_text(encoding="utf-8", errors="ignore")
            entries = self._parse_html(html)
            if entries:
                all_outages.extend(entries)

        # Filter empty outages and areas
        filtered_outages = []
        for o in all_outages:
            o["areas"] = [a for a in o["areas"] if any(a.values())]
            if any([o.get("occurrence_datetime"), o.get("recovery_datetime"),
                    o.get("reason"), o.get("households_affected")]) and o["areas"]:
                filtered_outages.append(o)

        if not filtered_outages:
            print("[INFO] No valid outages found.")
            return

        output_file = self.processed_dir / f"shikoku_outages_{self.today_iso}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(filtered_outages, f, ensure_ascii=False, indent=2)

        print(f"\nParsed {len(filtered_outages)} outages → {output_file}")
        return output_file


if __name__ == "__main__":
    processor = ShikokuProcessor()
    processor.run()
