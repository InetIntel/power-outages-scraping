import json
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
from utils.upload import Uploader


class Process_Zhytomyr:
    def __init__(self, year, month, today, file=None):
        self.year = year
        self.month = month
        self.today = today
        self.file = file
        self.bucket_name = "ukraine"
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
        local_folder = f"./ukraine/zhytomyr/raw/{self.year}/{self.month}"
        os.makedirs(local_folder, exist_ok=True)

        if not self.uploader:
            print("Warning: uploader not initialized, will use local files only")
            return

        # List of rem_ids to download
        rem_ids = ['1', '2', '3', '4', '5', '7', '9', '11', '13', '14', '17', '18', '19', '20', '21', '23', '25']

        downloaded_count = 0
        for rem_id in rem_ids:
            file_name = f"power_outages.UA.zhytomyr.raw.{date}.{rem_id}.html"
            s3_path = f"ukraine/zhytomyr/raw/{self.year}/{self.month}/{file_name}"
            local_file_path = os.path.join(local_folder, file_name)

            # Skip if file already exists locally
            if os.path.exists(local_file_path):
                print(f"File already exists locally: {file_name}")
                continue

            try:
                self.uploader.download_file(s3_path, local_file_path)
                downloaded_count += 1
            except FileNotFoundError:
                print(f"File not found in S3: {s3_path}")
            except Exception as e:
                print(f"Error downloading {file_name}: {e}")

        print(f"Downloaded {downloaded_count} HTML files from S3")

    def parse_html_content(self, html_content):
        """Parse HTML content to extract power outage information"""
        soup = BeautifulSoup(html_content, 'html.parser')
        outages = []

        # Find all table rows (common pattern for outage data)
        tables = soup.find_all('table')

        for table in tables:
            rows = table.find_all('tr')

            for row in rows:
                cells = row.find_all(['td', 'th'])

                if len(cells) < 2:  # Skip header rows or incomplete rows
                    continue

                # Extract text from all cells
                cell_texts = [cell.get_text(strip=True) for cell in cells]

                # Try to parse outage information
                outage_info = self.extract_outage_info(cell_texts, row)
                if outage_info:
                    outages.append(outage_info)

        return outages

    def extract_outage_info(self, cell_texts, row):
        """Extract outage information from table cells"""
        try:
            # Look for date/time patterns
            date_pattern = r'(\d{1,2})[./](\d{1,2})[./](\d{4})'
            time_pattern = r'(\d{1,2}):(\d{2})'

            dates_found = []
            times_found = []
            address = ""
            category = "Planned"  # Default category

            full_text = ' '.join(cell_texts)

            # Extract dates
            date_matches = re.findall(date_pattern, full_text)
            for match in date_matches:
                day, month, year = match
                dates_found.append(f"{year}-{month.zfill(2)}-{day.zfill(2)}")

            # Extract times
            time_matches = re.findall(time_pattern, full_text)
            for match in time_matches:
                hour, minute = match
                times_found.append(f"{hour.zfill(2)}:{minute}")

            # Look for address/location information
            for cell_text in cell_texts:
                # Ukrainian street/address indicators
                if any(keyword in cell_text.lower() for keyword in ['вул', 'провул', 'площ', 'бульв', 'просп']):
                    address = cell_text
                    break

            # Determine category based on keywords
            if any(keyword in full_text.lower() for keyword in ['аварій', 'аварий', 'emergency']):
                category = "Emergency"
            elif any(keyword in full_text.lower() for keyword in ['план', 'planned']):
                category = "Planned"

            # If we found at least one date and time, create an outage entry
            if dates_found and times_found:
                start_date = dates_found[0]
                start_time = times_found[0] if times_found else "00:00"

                # If we have two dates/times, second is the end
                if len(dates_found) > 1:
                    end_date = dates_found[1]
                else:
                    end_date = start_date

                if len(times_found) > 1:
                    end_time = times_found[1]
                else:
                    end_time = times_found[0] if times_found else "00:00"

                start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
                end_datetime = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")

                # Calculate duration
                duration = (end_datetime - start_datetime).total_seconds() / 3600

                # Extract areas affected from address
                areas_affected = [address] if address else []

                return {
                    "start": start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                    "end": end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                    "duration_(hours)": "{:.2f}".format(max(duration, 0)),
                    "event_category": category,
                    "country": "Ukraine",
                    "areas_affected": areas_affected,
                }

        except Exception as e:
            # Skip rows that can't be parsed
            pass

        return None

    def get_data(self):
        """Load individual HTML files and process them"""
        folder = f"./ukraine/zhytomyr/raw/{self.year}/{self.month}"

        if not os.path.exists(folder):
            print(f"Folder not found: {folder}")
            return []

        # List of rem_ids to process
        rem_ids = ['1', '2', '3', '4', '5', '7', '9', '11', '13', '14', '17', '18', '19', '20', '21', '23', '25']

        res = []

        for rem_id in rem_ids:
            html_file = f"power_outages.UA.zhytomyr.raw.{self.today}.{rem_id}.html"
            html_path = os.path.join(folder, html_file)

            if not os.path.exists(html_path):
                print(f"HTML file not found: {html_file}")
                continue

            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()

                outages = self.parse_html_content(html_content)
                res.extend(outages)
                print(f"processed {len(outages)} outages from rem_id: {rem_id}")
            except Exception as e:
                print(f"error processing rem_id {rem_id}: {e}")
                continue

        return res

    def check_folder(self, type):
        self.folder_path = (
                "./ukraine/zhytomyr/" + type + "/" + self.year + "/" + self.month
        )
        os.makedirs(self.folder_path, exist_ok=True)

    def save_json(self, data):
        self.check_folder("processed")
        file_name = f"power_outages.UA.zhytomyr.processed.{self.today}.json"
        file_path = os.path.join(self.folder_path, file_name)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"saved processed data to: {file_path}")

        if self.uploader:
            s3_path = f"ukraine/zhytomyr/processed/{self.year}/{self.month}/{file_name}"
            try:
                self.uploader.upload_file(file_path, s3_path)
                print(f"uploaded processed file to S3: {s3_path}")
            except Exception as e:
                print(f"error uploading processed file: {e}")

    def run(self, date=None):
        try:
            self.download_raw_files(date)
        except Exception as e:
            print(f"failed to download raw files: {e}")
            # Continue anyway - might have local files

        data = self.get_data()

        if data:
            self.save_json(data)
        else:
            print("no outage data extracted")


if __name__ == "__main__":
    import sys

    # python post_process_zhytomyr.py [YYYY-MM-DD]
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

    processor = Process_Zhytomyr(year, month, date)
    processor.run(date)