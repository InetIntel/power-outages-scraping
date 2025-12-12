import json
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import datetime

class OkinawaProcessor:
    """Post-process Okinawa XML files into structured JSON."""

    def __init__(self):
        self.base_path = Path(__file__).resolve().parent / "data" / "raw"
        self.output_path = self.base_path.parent / "processed"
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.output_file = self.output_path / "okinawa_processed.json"

    def parse_xml_file(self, xml_path):
        """Parse a single Okinawa XML file."""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except ET.ParseError as e:
            print(f"[WARN] Failed to parse {xml_path}: {e}")
            return []

        outages = []

        for town in root.findall(".//town"):
            try:
                city_town = town.attrib.get("name", "").strip()
                power_cut_date = town.findtext("power_cut_date", "").strip()
                power_cut_time = town.findtext("power_cut_time", "").strip()
                send_finish_date = town.findtext("send_finish_date", "").strip()
                send_finish_time = town.findtext("send_finish_time", "").strip()
                restoration_area = town.findtext("restoration_area", "").strip()
                households = town.findtext("restoration_house", "").strip()
                equipment = town.findtext("equipment", "").strip()
                reason = town.findtext("reason", "").strip()

                if not (power_cut_date and power_cut_time and send_finish_date and send_finish_time):
                    continue  # skip incomplete entries

                # Combine date + time into ISO format
                try:
                    occurrence_dt = datetime.strptime(power_cut_date + " " + power_cut_time, "%Y.%m.%d %H:%M")
                    occurrence_iso = occurrence_dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    occurrence_iso = f"{power_cut_date} {power_cut_time}"

                try:
                    recovery_dt = datetime.strptime(send_finish_date + " " + send_finish_time, "%Y.%m.%d %H:%M")
                    recovery_iso = recovery_dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    recovery_iso = f"{send_finish_date} {send_finish_time}"

                # Skip entries with "-" or empty areas
                if restoration_area == "−" or not restoration_area:
                    restoration_area = ""

                outages.append({
                    "time_of_occurrence": occurrence_iso,
                    "recovery_time": recovery_iso,
                    "restoration_area": restoration_area,
                    "num_restored_homes": households,
                    "reason": reason,
                    "city_town": city_town,
                    "equipment_cause": equipment
                })

            except Exception as e:
                print(f"[WARN] Failed to parse town entry in {xml_path}: {e}")

        return outages

    def run(self):
        all_outages = []
        for xml_file in sorted(self.base_path.glob("*.xml")):
            print(f"[PROCESS] Parsing {xml_file.name}")
            outages = self.parse_xml_file(xml_file)
            all_outages.extend(outages)

        if not all_outages:
            print("[WARN] No outages found.")
            return

        # Save combined JSON
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(all_outages, f, ensure_ascii=False, indent=2)

        print(f"[OKINAWA] Saved {len(all_outages)} outages → {self.output_file.name}")
        return self.output_file


if __name__ == "__main__":
    processor = OkinawaProcessor()
    processor.run()
