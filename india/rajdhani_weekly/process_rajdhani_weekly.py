import json
import os
from bs4 import BeautifulSoup


class Process_rajdhani_weekly:

    def __init__(self, year, month, today, file):
        self.year = year
        self.month = month
        self.today = today
        self.file = file

    def get_table(self):
        with open(self.file, "r", encoding="utf-8") as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Find table with proper validation
        table = soup.find("tbody", {"id": "billDetailsData"})
        if not table:
            print("No table with id 'billDetailsData' found in HTML")
            return None
        
        return table

    def process(self, table):
        res = []
        all_tr = table.find_all("tr")
        
        if not all_tr or len(all_tr) < 2:
            print("No table rows found or insufficient data")
            return []
        
        # Extract headers
        titles = [td.get_text(strip=True) for td in all_tr[1].find_all(["td", "th"])]
        
        if not titles:
            print("No table headers found")
            return []
        
        # Process data rows
        for tr in all_tr[2:]:
            row_data = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            
            # Skip no-data rows
            if row_data == ['No data found for todays date.'] or not row_data:
                continue
            
            # Ensure we have matching data and titles
            if len(row_data) != len(titles):
                print(f"Warning: Row data length ({len(row_data)}) doesn't match titles length ({len(titles)})")
                continue
            
            data = {}
            for i in range(len(titles)):
                data[titles[i]] = row_data[i]
            
            # Add metadata
            data["country"] = "India"
            data["data_type"] = "weekly_dashboard"
            data["date"] = self.today
            
            res.append(data)
        
        return res

    def check_folder(self, type):
        self.folder_path = "./india/rajdhani_weekly/" + type + "/" + self.year + "/" + self.month
        os.makedirs(self.folder_path, exist_ok=True)

    def save_json(self, data):
        self.check_folder("processed")
        file_path = os.path.join(self.folder_path,
                                 "power_outages.IND.rajdhani_weekly.processed." + self.today + ".json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def run(self):
        table = self.get_table()
        
        # Handle case with no table
        if not table:
            print(f"No table data found for Rajdhani_weekly on {self.today}")
            # Still save an empty processed file
            self.save_json([])
            return
        
        data = self.process(table)
        
        # Handle case with no data
        if not data:
            print(f"No processed data found for Rajdhani_weekly on {self.today}")
            # Still save an empty processed file
            self.save_json([])
        else:
            self.save_json(data)
            print(f"Data is processed for Rajdhani_weekly. Found {len(data)} records.")


if __name__ == "__main__":
    file = ""
    file_list = file.split(".")
    date = file_list[-2]
    date_list = date.split("-")
    year = date_list[0]
    month = date_list[1]
    process = Process_rajdhani_weekly(year, month, date, file)
    process.run()