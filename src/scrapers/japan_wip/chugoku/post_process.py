import os
import re
import json
from bs4 import BeautifulSoup

class ChugokuPostProcessor:
    """
    Parses saved raw HTML files for power outage data from Chugoku Electric.
    Converts the HTML into structured JSON.
    """

    def __init__(self):
        self.provider = "chugoku"
        self.country_code = "JP"
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, "data")
        self.processed_dir = os.path.join(self.base_dir, "processed")
        os.makedirs(self.processed_dir, exist_ok=True)

    def parse_html(self, file_path: str):
        """Parse a single raw HTML file and extract outage information."""
        with open(file_path, "r", encoding="utf-8") as f:
            html = f.read()

        soup = BeautifulSoup(html, "html.parser")
        outages = []

        # Find all rows that likely contain outage data
        # (Example: <tr><td>City</td><td>123</td><td>10:05</td><td>12:00</td></tr>)
        for row in soup.find_all("tr"):
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cols) >= 2 and re.search(r"\d+", "".join(cols)):  # crude filter
                outage = {
                    "city": cols[0],
                    "affected_households": cols[1],
                    "start_time": cols[2] if len(cols) > 2 else None,
                    "expected_recovery": cols[3] if len(cols) > 3 else None,
                }
                outages.append(outage)

        print(f"[PROCESS] Found {len(outages)} outages in {os.path.basename(file_path)}")
        return outages

    def process_latest(self):
        """Automatically process the most recent raw HTML file."""
        html_files = [
            f for f in os.listdir(self.data_dir)
            if f.endswith(".html") and self.provider in f
        ]
        if not html_files:
            raise FileNotFoundError("No raw HTML files found in data/")

        latest_file = max(
            html_files,
            key=lambda f: os.path.getmtime(os.path.join(self.data_dir, f))
        )
        latest_path = os.path.join(self.data_dir, latest_file)

        outages = self.parse_html(latest_path)

        # Save processed JSON
        json_filename = latest_file.replace(".html", ".json")
        output_path = os.path.join(self.processed_dir, json_filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(outages, f, ensure_ascii=False, indent=2)

        print(f"[PROCESS] Saved structured JSON → {output_path}")
        return output_path


if __name__ == "__main__":
    processor = ChugokuPostProcessor()
    processor.process_latest()
