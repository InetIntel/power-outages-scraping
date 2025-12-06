def ask_chatgpt_for_outage_page(country):
    prompt = (
        f"""You are a data scraper assistant.
Return a JSON array of all **power supply companies** data operating in {country} as a list.

For each company, strictly return JSON objects in this format:


[
  {{
    "Company / Data source": "Company Name",
    "Region": "Area in which the company operates",
    "Description": "What kind of power outage data the site provides (if no data, mention 'No outage data available')",
    "Comments on Web Scraping": "Step-by-step manual scraping method or 'Not applicable' if no data",
    "Power Outage Link": "URL of the official company page where outage data is (if none, use 'N/A'), Please provide the specific page not homepage",
    "Website": "URL of the homepage of the official company website",
    "Official Government Website URL": "URL of the official government website page where we got this company info",
    "Scraping code created": "no",
    "Challenges": "Challenges faced in scraping the data (or 'No challenges' if none)",
    "Data Type": "Future | Historical | Excel | None",
    "Scraping Frequency": "what is the frequency of data update? daily | weekly | monthly",
    "Status": "Not Started"
  }},
  ...
]
⚠️ Very Important:
- Include **all companies** in {country} even if they do not provide outage data.
- also scrape website if its in non english language.
- Return only a valid JSON array, no explanation text outside JSON.
    """)
    
    return prompt
