import json
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
from utils.upload import Uploader


class Process_MEA:
    def __init__(self, year, month, today, file=None):
        self.year = year
        self.month = month
        self.today = today
        self.file = file
        self.bucket_name = "thailand"
        try:
            self.uploader = Uploader(self.bucket_name)
        except Exception as e:
            print(f"error initializing uploader: {e}")
            self.uploader = None

    def download_raw_files(self, date=None):
        """Download all individual HTML files from S3"""
        if date is None:
            date = self.today
        else:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            self.year = str(date_obj.year)
            self.month = str(date_obj.month).zfill(2)
            self.today = date

        # Create local folder structure
        local_folder = f"./thailand/mea/raw/{self.year}/{self.month}"
        os.makedirs(local_folder, exist_ok=True)

        if not self.uploader:
            print("Uploader not initialized, will use local files only")
            return

        # List all files in the S3 folder for this date
        s3_prefix = f"thailand/mea/raw/{self.year}/{self.month}/"

        try:
            # List all objects with the given prefix
            response = self.uploader.client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=s3_prefix
            )

            if "Contents" not in response:
                print(f"No files found in S3 with prefix: {s3_prefix}")
                return

            downloaded_count = 0

            for obj in response["Contents"]:
                file_key = obj["Key"]

                # Check if this file matches our date
                if f".{date}." in file_key:
                    file_name = os.path.basename(file_key)
                    local_file_path = os.path.join(local_folder, file_name)

                    # Skip if file already exists locally
                    if os.path.exists(local_file_path):
                        continue

                    try:
                        self.uploader.download_file(file_key, local_file_path)
                        downloaded_count += 1
                    except Exception as e:
                        print(f"Error downloading {file_name}: {e}")

            print(f"Downloaded {downloaded_count} HTML files from S3")
        except Exception as e:
            print(f"Error listing/downloading files: {e}")

    def clean_text(self, element):
        """
        Extract text from an element preserving whitespace structure,
        then normalize to single spaces.
        """
        if not element:
            return ""
        # get_text() without strip=True preserves spaces between tags/text nodes
        text_raw = element.get_text()
        # Replace non-breaking spaces and invisible characters with standard space
        text = text_raw.replace("\xa0", " ")
        # Collapse multiple spaces into one and strip ends
        return re.sub(r"\s+", " ", text).strip()

    def parse_html_content(self, html_content, announcement_id):
        """Parse HTML content to extract power outage information"""
        soup = BeautifulSoup(html_content, "html.parser")
        outages = []

        # Find the content description div
        content_div = soup.find("div", class_="content-description")

        if not content_div:
            print(f"No content found in announcement {announcement_id}")
            return outages

        # Extract all paragraphs
        paragraphs = content_div.find_all("p", class_="MsoNormal")

        current_date = None
        current_location = None
        current_time_range = None

        # Regex Patterns
        # Date: Matches "Saturday, Dec 6, 2025" or "Saturday, Dec 6 , 2025"
        date_pattern = re.compile(
            r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+([A-Za-z]+)\.?\s+(\d{1,2})\s*,?\s+(\d{4})",
            re.IGNORECASE,
        )
        # Location: Matches "Bangkok/Nonthaburi/Samutprakan/Pathum Thani : The power outage..."
        location_pattern = re.compile(
            r"(Bangkok|Nonthaburi|Samutprakan|Pathum Thani)\s*:?\s*The power outage areas are",
            re.IGNORECASE,
        )
        # Time: Matches "08.00 AM - 01.00 PM"
        time_pattern = re.compile(
            r"(\d{1,2})[:\.](\d{2})\s*(AM|PM)\s*[\-–—]\s*(\d{1,2})[:\.](\d{2})\s*(AM|PM)",
            re.IGNORECASE,
        )

        for p in paragraphs:
            text = self.clean_text(p)

            if not text:
                continue

            # 1. Check for Date
            date_match = date_pattern.search(text)
            if date_match:
                month_str, day, year = date_match.groups()
                current_date = self.parse_date(month_str, day, year)
                # Reset areas when date changes
                continue

            # 2. Check for Location
            location_match = location_pattern.search(text)
            if location_match:
                current_location = location_match.group(1)
                continue

            # 3. Check for Time
            time_match = time_pattern.search(text)
            if time_match:
                start_hour, start_min, start_period, end_hour, end_min, end_period = (
                    time_match.groups()
                )
                current_time_range = {
                    "start": f"{start_hour.zfill(2)}:{start_min} {start_period}",
                    "end": f"{end_hour.zfill(2)}:{end_min} {end_period}",
                }
                continue

            # 4. Check for areas
            if (
                text.startswith("-")
                and current_date
                and current_location
                and current_time_range
            ):
                area_text = text[1:].strip()

                # Create an outage entry
                outage = self.create_outage_entry(
                    current_date, current_location, current_time_range, area_text
                )

                if outage:
                    outages.append(outage)

        return outages

    def parse_date(self, month_str, day, year):
        """Convert month string to date"""
        month_map = {
            "jan": "01",
            "january": "01",
            "feb": "02",
            "february": "02",
            "mar": "03",
            "march": "03",
            "apr": "04",
            "april": "04",
            "may": "05",
            "jun": "06",
            "june": "06",
            "jul": "07",
            "july": "07",
            "aug": "08",
            "august": "08",
            "sep": "09",
            "september": "09",
            "oct": "10",
            "october": "10",
            "nov": "11",
            "november": "11",
            "dec": "12",
            "december": "12",
        }

        month_num = month_map.get(month_str.lower(), "01")
        formatted_date = f"{year}-{month_num}-{day.zfill(2)}"
        return formatted_date

    def convert_to_24h(self, time_str, period):
        """Convert 12-hour time to 24-hour format"""
        hour, minute = time_str.split(":")
        hour = int(hour)

        if period.upper() == "PM" and hour != 12:
            hour += 12
        elif period.upper() == "AM" and hour == 12:
            hour = 0

        return f"{hour:02d}:{minute}"

    def create_outage_entry(self, date, location, time_range, area):
        """Create a structured outage entry"""
        try:
            # Parse time range
            start_match = re.match(r"(\d{2}):(\d{2})\s+(AM|PM)", time_range["start"])
            end_match = re.match(r"(\d{2}):(\d{2})\s+(AM|PM)", time_range["end"])

            if not start_match or not end_match:
                return None

            start_time = self.convert_to_24h(
                f"{start_match.group(1)}:{start_match.group(2)}", start_match.group(3)
            )
            end_time = self.convert_to_24h(
                f"{end_match.group(1)}:{end_match.group(2)}", end_match.group(3)
            )

            start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            end_datetime = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")

            # Handle case where end time is next day
            if end_datetime < start_datetime:
                pass

            duration = (end_datetime - start_datetime).total_seconds() / 3600

            return {
                "start": start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "end": end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_(hours)": "{:.2f}".format(max(duration, 0)),
                "event_category": "Planned",
                "country": "Thailand",
                "region": location,
                "areas_affected": [area],
            }

        except Exception as e:
            print(f"Error creating outage entry for date {date}: {e}")
            return None

    def get_data(self):
        """Load individual HTML files and process them"""
        folder = f"./thailand/mea/raw/{self.year}/{self.month}"

        if not os.path.exists(folder):
            print(f"Folder not found: {folder}")
            return []

        res = []

        # Get all HTML files for today
        html_files = [
            f
            for f in os.listdir(folder)
            if f.endswith(".html") and f".{self.today}." in f
        ]

        print(f"Found {len(html_files)} HTML files to process")

        for html_file in html_files:
            html_path = os.path.join(folder, html_file)
            announcement_id = html_file.split(".")[-2]

            try:
                with open(html_path, "r", encoding="utf-8") as f:
                    html_content = f.read()

                outages = self.parse_html_content(html_content, announcement_id)
                res.extend(outages)
                print(
                    f"Processed {len(outages)} outages from announcement: {announcement_id}"
                )
            except Exception as e:
                print(f"Error processing announcement {announcement_id}: {e}")
                continue

        return res

    def check_folder(self, type):
        self.folder_path = "./thailand/mea/" + type + "/" + self.year + "/" + self.month
        os.makedirs(self.folder_path, exist_ok=True)

    def save_json(self, data):
        self.check_folder("processed")
        file_name = f"power_outages.TH.mea.processed.{self.today}.json"
        file_path = os.path.join(self.folder_path, file_name)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Saved processed data to: {file_path}")

        if self.uploader:
            s3_path = f"thailand/mea/processed/{self.year}/{self.month}/{file_name}"
            try:
                self.uploader.upload_file(file_path, s3_path)
                print(f"Uploaded processed file to S3: {s3_path}")
            except Exception as e:
                print(f"Error uploading processed file: {e}")

    def run(self, date=None):
        """Main processing workflow"""

        # Download raw files from S3
        try:
            self.download_raw_files(date)
        except Exception as e:
            print(f"Failed to download raw files: {e}")

        # Process the HTML files
        data = self.get_data()

        # Save processed data
        if data:
            self.save_json(data)
            print(f"Completed: {len(data)} records")
        else:
            print("No outage data saved")


if __name__ == "__main__":
    import sys

    # python post_process.py [YYYY-MM-DD]
    date = sys.argv[1] if len(sys.argv) > 1 else None

    if date:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        year = str(date_obj.year)
        month = str(date_obj.month).zfill(2)
    else:
        today = datetime.today()
        year = str(today.year)
        month = str(today.month).zfill(2)
        date = today.strftime("%Y-%m-%d")

    processor = Process_MEA(year, month, date)
    processor.run(date)
