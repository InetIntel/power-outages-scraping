import os
import json
from pathlib import Path
from bs4 import BeautifulSoup


BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = PROCESSED_DIR / "combined_chugoku_processed.json"


def parse_event_block(ul):
    """
    Parse one <ul class="js-knm"> block.
    It contains:
        - Event metadata table (発生日時 / 復旧日時 / 停電理由 / 停電戸数)
        - Area list grouped by prefecture → city → areas
    """
    event = {
        "occurrence": None,
        "recovery": None,
        "reason": None,
        "households": None,
        "areas": []
    }

    lis = ul.find_all("li", recursive=False)

    # 1. Extract event metadata
    in_event_table = False
    for li in lis:
        divs = li.find_all("div", recursive=False)
        if any("発生日時" in d.get_text() for d in divs):
            in_event_table = True
            continue
        if in_event_table:
            if len(divs) >= 4:
                event["occurrence"] = divs[0].get_text(strip=True)
                event["recovery"] = divs[1].get_text(strip=True)
                event["reason"] = divs[2].get_text(strip=True)
                event["households"] = divs[3].get_text(strip=True)
            in_event_table = False
            continue

    # 2. Extract areas
    for li in lis:
        if "js-tdk" in li.get("class", []):
            prefecture = li.get("data-tdk", "").strip()
            inner_ul = li.find("ul")
            if not inner_ul:
                continue
            for scg in inner_ul.find_all("li", class_="js-scg"):
                city = scg.get("data-scg", "").strip()
                areas = [span.get("data-jsy", "").strip() for span in scg.find_all("span", class_="js-jsy") if span.get("data-jsy", "").strip()]
                for area in areas:
                    event["areas"].append({
                        "prefecture": prefecture,
                        "city": city,
                        "area": area
                    })

    return event


def parse_html_file(filepath):
    """Parse one HTML file for multiple event blocks."""
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    results = []

    blocks = soup.select("ul.js-knm.p-table-list")
    for ul in blocks:
        event = parse_event_block(ul)
        results.append(event)

    return results


def run():
    all_events = []

    for file in sorted(RAW_DIR.glob("*.html")):
        print(f"[PROCESS] {file.name}")
        events = parse_html_file(file)
        all_events.extend(events)

    # Save combined file
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print(f"\n[SAVED] {OUTPUT_FILE}")
    print(f"Total events: {len(all_events)}")


if __name__ == "__main__":
    run()
