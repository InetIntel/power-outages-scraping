import os
import json
from datetime import datetime
from openai import OpenAI

OPENAI_API_KEY = "YOUR_OPENAI"

class Processor:

    def __init__(self, key):

        self.client = OpenAI(api_key=key)

        self.provider = "nesco"
        self.country = "bangladesh"

        target_date = datetime.now()
        self.today = target_date.strftime("%Y-%m-%d")
        self.year = target_date.strftime("%Y")
        self.month = target_date.strftime("%m")
        self.day = target_date.strftime("%d")

        self.raw_filename = f"power_outages.BD.{self.provider}.raw.{self.today}.json"
        self.processed_filename = f"power_outages.BD.{self.provider}.processed.{self.today}.json"

        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.raw_folder_path = os.path.join(self.script_dir, "raw", self.year, self.month)
        self.processed_folder_path = os.path.join(self.script_dir, "processed", self.year, self.month)

    def extract_record(self, text):
        prompt = f"""
    Extract structured information from the following power outage announcement and translate if not in English.

    OUTPUT STRICTLY AS VALID JSON. Do not add comments or explanations.

    Required JSON fields:
    - country: "Bangladesh"
    - start: "YYYY-MM-DD_HH-MM-SS"
    - end: "YYYY-MM-DD_HH-MM-SS"
    - duration_hours: numeric
    - event_category: choose one of ["Routine maintenance", "Emergency repair", "Tree trimming", "General outage"]
    - area_affected: dictionary with keys = broader region, values = list of affected specific areas.

    Text:
    \"\"\"{text}\"\"\"
    """

        response = self.client.responses.create(
            model="gpt-5-nano",
            input=prompt,
            # response_format={"type": "json_object"}
        )
        # print(response.output_text)
        return json.loads(response.output_text)


    def process(self):
        with open(os.path.join(self.raw_folder_path, self.raw_filename), "r") as f:
            raw_data = json.load(f)

        structured = []

        print(f"Processing {len(raw_data)} records from {self.raw_filename}")

        for idx, record in enumerate(raw_data):
            title_text = record["বিষয়বস্তু"]
            print(f"Processing record {idx+1}/{len(raw_data)}")
            result_json = self.extract_record(title_text)
            structured.append(result_json)

        os.makedirs(self.processed_folder_path, exist_ok=True)
        with open(os.path.join(self.processed_folder_path, self.processed_filename), "w") as f:
            json.dump(structured, f, indent=2)

        print(f"Saved {self.processed_filename}")

if __name__ == "__main__":
    processor = Processor(OPENAI_API_KEY)
    processor.process()
