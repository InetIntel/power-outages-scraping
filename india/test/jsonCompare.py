import json
import os

def are_json_files_equal(file1, file2):
    try:
        with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
            json1 = json.load(f1)
            json2 = json.load(f2)

        return json1 == json2  # Compares JSON content
    except Exception as e:
        print(f"Error: {e}")
        return False

# Example Usage
dates=['2025-02-20','2025-02-21','2025-02-22','2025-02-23','2025-02-24','2025-02-25','2025-02-26']
for i in range(len(dates)-1):
    file1 = "./"+dates[i]+"/BSES_Rajdhani_outage_26-02-2025.json"
    file2 = "./"+dates[i+1]+"/BSES_Rajdhani_outage_26-02-2025.json"

    if not os.path.exists(file1):
        continue
    if not os.path.exists(file2):
        continue

    if are_json_files_equal(file1, file2):
        pass
    else:
        print("The JSON files are different."+f"{dates[i]} and {dates[i+1]}")
