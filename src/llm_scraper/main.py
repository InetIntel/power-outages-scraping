import requests
import time
import threading
import os
import json
import re
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from notion_client import Client
from openai import OpenAI
from dotenv import load_dotenv
from prompt import ask_chatgpt_for_outage_page

"""
Main script to fetch all countries from IODA API and create Notion tables for each country.
This orchestrates the entire process of country discovery and Notion database setup.

Usage:
    python main.py                    # add all country databases (NO scraping)
    python main.py --country Brazil   # add page and table for Brazil (No Scraping)
    python main.py --country India --scrape  # add page and table and scrape data for India
    python main.py --scrape           # Scrape data for all countries
    python main.py --scrape-only      # Scrape all countries (skip DB creation)
    python main.py --help             # Show this help message
"""

# Load environment variables
load_dotenv()

# ============================================================================
# MODEL CONFIGURATION - Change these to use different GPT models
# ============================================================================
# Web scraping model (used for searching and gathering data)
WEB_SEARCH_MODEL = os.getenv('WEB_SEARCH_MODEL', 'gpt-4o-mini')

# Parsing model (used for formatting and parsing JSON)
PARSING_MODEL = os.getenv('PARSING_MODEL', 'gpt-4o-mini')

# To use different models, either:
# 1. Set environment variables: 
#    $env:WEB_SEARCH_MODEL="gpt-4o"
#    $env:PARSING_MODEL="gpt-4o-mini"
# 2. Or edit the defaults above directly

print(f"Model Configuration:")
print(f"  Web Search Model: {WEB_SEARCH_MODEL}")
print(f"  Parsing Model: {PARSING_MODEL}")
print()

# ============================================================================

# IODA API configuration
IODA_API_URL = "https://api.ioda.inetintel.cc.gatech.edu/v2/entities/query"

# Global storage
country_to_region = {}
lock = threading.Lock()


def fetch_countries():
    """
    Fetch all countries from IODA API.
    
    Returns:
        dict: {country_name: country_code}
    """
    print("Fetching countries from IODA API...")
    
    params = {"entityType": "country"}
    headers = {"accept": "*/*"}
    
    try:
        response = requests.get(IODA_API_URL, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        country_to_code = {
            country["name"]: country["code"] 
            for country in data["data"]
        }
        
        print(f"[OK] Fetched {len(country_to_code)} countries")
        return country_to_code
        
    except Exception as e:
        print(f"[ERROR] Error fetching countries: {e}")
        return {}


def fetch_regions_for_country(country_name, country_code):
    """
    Fetch all regions for a specific country.
    
    Args:
        country_name: Name of the country
        country_code: Country code from IODA API
    """
    params = {
        "entityType": "region",
        "relatedTo": f"country/{country_code}"
    }
    headers = {"accept": "*/*"}
    
    try:
        response = requests.get(IODA_API_URL, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            region_names = [region["name"] for region in data.get("data", [])]
            
            with lock:
                country_to_region[country_name] = region_names
                
            print(f"  [OK] {country_name}: {len(region_names)} regions")
        else:
            print(f"  [ERROR] {country_name}: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"  [ERROR] {country_name}: {e}")


def fetch_all_regions(country_to_code, max_workers=5):
    """
    Fetch regions for all countries concurrently.
    
    Args:
        country_to_code: Dictionary mapping country names to codes
        max_workers: Number of concurrent threads
    """
    print(f"\nFetching regions for all countries (using {max_workers} workers)...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(fetch_regions_for_country, country_name, country_code)
            for country_name, country_code in country_to_code.items()
        ]
        
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"  [ERROR] Thread error: {e}")
    
    print(f"[OK] Completed fetching regions for {len(country_to_region)} countries\n")


def get_existing_databases(notion_client, page_id):
    """
    Get all child databases on a Notion page.
    
    Args:
        notion_client: Notion client instance
        page_id: Notion page ID
        
    Returns:
        dict: {database_title: database_id}
    """
    databases = {}
    has_more = True
    start_cursor = None
    
    while has_more:
        response = notion_client.blocks.children.list(
            block_id=page_id,
            start_cursor=start_cursor
        )
        
        for block in response["results"]:
            if block["type"] == "child_database":
                title = block["child_database"]["title"].strip()
                databases[title] = block["id"]
        
        has_more = response.get("has_more", False)
        start_cursor = response.get("next_cursor")
    
    return databases


def create_notion_database(notion_client, main_page_id, country_name, existing_databases):
    """
    Create a Notion database for a country if it doesn't already exist.
    
    Args:
        notion_client: Notion client instance
        main_page_id: Parent page ID in Notion
        country_name: Name of the country
        existing_databases: Dictionary of existing database titles to IDs
        
    Returns:
        str: Database ID if created/exists, None on error
    """
    try:
        if country_name in existing_databases:
            print(f"  [SKIP] {country_name}: Already exists")
            return existing_databases[country_name]
        
        
        database = notion_client.databases.create(
            parent={"type": "page_id", "page_id": main_page_id},
            title=[{"type": "text", "text": {"content": country_name}}],
            initial_data_source={
                "properties": {
                    "Company / Data source": {"title": {}},
                    "Region": {"rich_text": {}},
                    "Description": {"rich_text": {}},
                    "Comments on Web Scraping": {"rich_text": {}},
                    "Link": {"rich_text": {}},
                    "Website": {"rich_text": {}},
                    "Official Government Website URL": {"rich_text": {}},
                    "Scraping code created": {"rich_text": {}},
                    "Challenges": {"multi_select": {"options": []}},
                    "Data Type": {"multi_select": {"options": []}},
                    "Scraping Frequency": {"multi_select": {"options": []}},
                    "Status": {"multi_select": {"options": []}}
                }
            }
        )
        
        db_id = database["id"]
        print(f"  [OK] {country_name}: Created database")
        return db_id
        
    except Exception as e:
        print(f"  [ERROR] {country_name}: Error - {e}")
        return None


def create_all_notion_databases(country_to_region, max_workers=3):
    """
    Create Notion databases for all countries concurrently.
    
    Args:
        country_to_region: Dictionary mapping country names to region lists
        max_workers: Number of concurrent threads
        
    Returns:
        list: List of created database IDs
    """
    # Initialize Notion client
    notion_token = os.getenv('NOTION_TOKEN')
    main_page_id = os.getenv('MAIN_PAGE_ID')
    
    if not notion_token or not main_page_id:
        print("[ERROR] NOTION_TOKEN and MAIN_PAGE_ID must be set in .env file")
        return []
    
    notion = Client(auth=notion_token)
    
    print(f"Creating Notion databases (using {max_workers} workers)...")
    
    # Get existing databases
    existing_databases = get_existing_databases(notion, main_page_id)
    print(f"Found {len(existing_databases)} existing databases\n")
    
    created_database_ids = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                create_notion_database,
                notion,
                main_page_id,
                country_name,
                existing_databases
            )
            for country_name in country_to_region.keys()
        ]
        
        for future in as_completed(futures):
            try:
                db_id = future.result()
                if db_id:
                    created_database_ids.append(db_id)
            except Exception as e:
                print(f"  [ERROR] Thread error: {e}")
    
    print(f"\n[OK] Created/verified {len(created_database_ids)} Notion databases")
    return created_database_ids


def parse_chatgpt_output_with_llm(raw_output, country_name):
    """
    Use LLM to parse and structure ChatGPT output into proper JSON format.
    
    Args:
        raw_output: Raw text output from ChatGPT
        country_name: Name of the country (for logging)
        
    Returns:
        list: Parsed and structured data, or empty list on error
    """
    try:
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            print(f"  [ERROR] {country_name}: OPENAI_API_KEY not set")
            return []
        
        client = OpenAI(api_key=openai_api_key)
        
        # Use cheaper model to parse the output
        print(f"  [INFO] {country_name}: Parsing output with LLM...")
        
        parse_response = client.chat.completions.create(
            model=PARSING_MODEL,  # Use configured parsing model
            messages=[
                {
                    "role": "system",
                    "content": """You are a JSON formatter. Your job is to take messy text data and convert it to a valid JSON array.
Return ONLY a valid JSON array with the following structure:
[
    {
        "Company / Data source": "string",
        "Region": "string",
        "Description": "string",
        "Comments on Web Scraping": "string",
        "Power Outage Link": "string",
        "Website": "string",
        "Official Government Website URL": "string",
        "Scraping code created": "string",
        "Challenges": "string",
        "Data Type": "string",
        "Scraping Frequency": "string",
        "Status": "string"
    }
]
Do NOT include markdown, code blocks, or any explanation. Only return pure JSON."""
                },
                {
                    "role": "user",
                    "content": f"Parse this data into JSON format:\n\n{raw_output}"
                }
            ],
            temperature=0.3  # Lower temperature for more consistent output
        )
        
        # Extract JSON from response
        json_output = parse_response.choices[0].message.content.strip()
        
        # Clean JSON output if wrapped in code blocks
        if json_output.startswith("```"):
            json_output = json_output.split("```json")[-1].split("```")[0].strip()
        if json_output.startswith("```"):
            json_output = json_output.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        data = json.loads(json_output)
        
        if not isinstance(data, list):
            print(f"  [WARN] {country_name}: Parser returned non-list, converting to list")
            data = [data] if isinstance(data, dict) else []
        
        print(f"  [OK] {country_name}: Parsed {len(data)} entries")
        return data
        
    except json.JSONDecodeError as e:
        print(f"  [ERROR] {country_name}: JSON parsing error - {e}")
        return []
    except Exception as e:
        print(f"  [ERROR] {country_name}: Parsing error - {e}")
        return []


def scrape_country_data_with_chatgpt(country_name):
    """
    Use ChatGPT with web search to scrape power company data for a country.
    
    Args:
        country_name: Name of the country to scrape
        
    Returns:
        list: List of company data dictionaries, or empty list on error
    """
    try:
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            print(f"  [ERROR] {country_name}: OPENAI_API_KEY not set")
            return []
        
        client = OpenAI(api_key=openai_api_key)
        
        # Get the prompt for this country
        prompt = ask_chatgpt_for_outage_page(country_name)
        
        # Step 1: Use web search to gather information
        print(f"  🔍 {country_name}: Searching web...")
        response = client.responses.create(
            model=WEB_SEARCH_MODEL,  # Use configured web search model
            tools=[{"type": "web_search"}],
            input=prompt,
        )
        
        # Extract the text from web search response
        web_search_text = response.output[-1].content[0].text
        return web_search_text
    except Exception as e:
        print(f"  [ERROR] {country_name}: Web search error - {e}")
        return []


def clean_multiselect_value(value):
    """Remove special characters not allowed in Notion multi_select values."""
    if not value:
        return "N/A"
    # Keep only alphanumerics, spaces, hyphens, and underscores
    cleaned = re.sub(r"[^A-Za-z0-9 _-]", "", value)
    return cleaned.strip()


def page_exists(notion_client, database_id, company_name, region):
    """Check if a page already exists in the database."""
    try:
        query = notion_client.databases.query(
            database_id=database_id,
            filter={
                "and": [
                    {
                        "property": "Company / Data source",
                        "title": {"equals": company_name}
                    },
                    {
                        "property": "Region",
                        "rich_text": {"equals": region}
                    }
                ]
            }
        )
        return len(query.get("results", [])) > 0
    except Exception:
        return False


def add_companies_to_notion(notion_client, database_id, country_name, companies_data):
    """
    Add scraped company data to the Notion database.
    
    Args:
        notion_client: Notion client instance
        database_id: Database ID to add data to
        country_name: Name of the country
        companies_data: List of company dictionaries
        
    Returns:
        int: Number of companies added
    """
    added_count = 0
    
    for company in companies_data:
        try:
            company_name = company.get("Company / Data source", "Unknown")
            region = company.get("Region", "Unknown")
            
            # Check if already exists
            if page_exists(notion_client, database_id, company_name, region):
                print(f"    [SKIP] Duplicate: {company_name} ({region})")
                continue
            
            # Create the page
            notion_client.pages.create(
                parent={"database_id": database_id},
                properties={
                    "Company / Data source": {
                        "title": [{"text": {"content": company_name}}]
                    },
                    "Region": {
                        "rich_text": [{"text": {"content": region}}]
                    },
                    "Description": {
                        "rich_text": [{"text": {"content": company.get("Description", "")}}]
                    },
                    "Comments on Web Scraping": {
                        "rich_text": [{"text": {"content": company.get("Comments on Web Scraping", "")}}]
                    },
                    "Link": {
                        "rich_text": [{"text": {"content": company.get("Power Outage Link", company.get("Link", ""))}}]
                    },
                    "Website": {
                        "rich_text": [{"text": {"content": company.get("Website", "")}}]
                    },
                    "Official Government Website URL": {
                        "rich_text": [{"text": {"content": company.get("Official Government Website URL", "")}}]
                    },
                    "Scraping code created": {
                        "rich_text": [{"text": {"content": company.get("Scraping code created", "no")}}]
                    },
                    "Challenges": {
                        "multi_select": [{"name": clean_multiselect_value(company.get("Challenges", ""))}]
                    },
                    "Data Type": {
                        "multi_select": [
                            {"name": clean_multiselect_value(dt.strip())}
                            for dt in company.get("Data Type", "None").split("|")
                            if dt.strip()
                        ]
                    },
                    "Scraping Frequency": {
                        "multi_select": [
                            {"name": clean_multiselect_value(company.get("Scraping Frequency", "Once"))}
                        ]
                    },
                    "Status": {
                        "multi_select": [{"name": clean_multiselect_value(company.get("Status", "Not Started"))}]
                    }
                }
            )
            
            added_count += 1
            print(f"    [OK] Added: {company_name} ({region})")
            
        except Exception as e:
            print(f"    [ERROR] Error adding {company.get('Company / Data source', 'Unknown')}: {e}")
    
    return added_count


def scrape_and_populate_all_countries(country_to_database, max_workers=2):
    """
    Scrape company data for all countries and populate Notion databases.
    It appends data to existing databases without deleting prior entries.
    Args:
        country_to_database: Dictionary mapping country names to database IDs
        max_workers: Number of concurrent workers
        
    Returns:
        dict: Statistics about the scraping process
    """
    notion_token = os.getenv('NOTION_TOKEN')
    if not notion_token:
        print("[ERROR] NOTION_TOKEN must be set in .env file")
        return {}
    
    notion = Client(auth=notion_token)
    
    print(f"\nScraping company data for all countries (using {max_workers} workers)...")
    print("This may take a while...\n")
    
    stats = {
        "countries_processed": 0,
        "total_companies_found": 0,
        "total_companies_added": 0,
        "errors": 0
    }
    
    def process_country(country_name, database_id):
        # Scrape data
        companies_data = scrape_country_data_with_chatgpt(country_name)
        print(f"  [INFO] {country_name}: Received {len(companies_data)} companies from ChatGPT Data:{str(companies_data)[:100]}...")
        if not companies_data:
            return country_name, 0, 0
        
        companies_data = parse_chatgpt_output_with_llm(companies_data, country_name)
        # Add to Notion
        added_count = add_companies_to_notion(notion, database_id, country_name, companies_data)
        
        return country_name, len(companies_data), added_count
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_country, country_name, db_id)
            for country_name, db_id in country_to_database.items()
        ]
        
        for future in as_completed(futures):
            try:
                country_name, found, added = future.result()
                stats["countries_processed"] += 1
                stats["total_companies_found"] += found
                stats["total_companies_added"] += added
                
                print(f"[OK] {country_name}: {added}/{found} companies added\n")
                
            except Exception as e:
                stats["errors"] += 1
                print(f"[ERROR] Error processing country: {e}\n")
    
    return stats


def main():
    """
    Main execution function with command-line argument support.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Power Outages Country Data - Full Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                    # Update all country databases (NO scraping)
    python main.py --country Brazil   # Scrape data for Brazil
    python main.py --country India --scrape  # Scrape data for India
    python main.py --scrape           # Scrape data for all countries
    python main.py --scrape-only      # Scrape all countries (skip DB creation)
    python main.py --help             # Show this help message
                """
    )
    
    parser.add_argument(
        '--country',
        type=str,
        default=None,
        help='Run pipeline for a specific country (e.g., "Brazil", "India")'
    )
    
    parser.add_argument(
        '--scrape',
        action='store_true',
        help='Enable scraping for all countries'
    )
    
    parser.add_argument(
        '--scrape-only',
        action='store_true',
        help='Skip database creation and only scrape data'
    )
    
    args = parser.parse_args()
    
    start_time = time.time()
    
    print("=" * 60)
    if args.country:
        print(f"Power Outages Country Data - {args.country}")
    else:
        print("Power Outages Country Data - Full Pipeline")
    print("=" * 60 + "\n")
    
    # Step 1: Fetch all countries
    country_to_code = fetch_countries()
    if not country_to_code:
        print("[ERROR] Failed to fetch countries. Exiting.")
        return

    # If --country is provided, filter to that country only
    if args.country:
        matching_countries = [c for c in country_to_code.keys() if c.lower() == args.country.lower()]
        if not matching_countries:
            print(f"[ERROR] Country '{args.country}' not found in IODA API.")
            print(f"Available countries: {len(country_to_code)}")
            return
        country_name = matching_countries[0]
        country_to_code = {country_name: country_to_code[country_name]}
        print(f"[OK] Running pipeline for: {country_name}\n")

    # Step 2: Fetch regions (skip if only scraping and DB exists)
    if not args.scrape_only:
        fetch_all_regions(country_to_code, max_workers=5)
        # Step 3: Create Notion databases
        created_databases = create_all_notion_databases(country_to_region, max_workers=3)
    else:
        # For scrape-only mode, still need to fetch regions
        fetch_all_regions(country_to_code, max_workers=5)

    # Step 4: Scrape and populate data (only if --scrape is provided)
    should_scrape = args.scrape

    if should_scrape:
        notion_token = os.getenv('NOTION_TOKEN')
        main_page_id = os.getenv('MAIN_PAGE_ID')

        if notion_token and main_page_id:
            notion = Client(auth=notion_token)
            existing_databases = get_existing_databases(notion, main_page_id)

            # Map countries to their database IDs
            country_to_database = {
                country: existing_databases[country]
                for country in country_to_region.keys()
                if country in existing_databases
            }

            if not country_to_database:
                print("[ERROR] No matching databases found in Notion.")
                print("  Run without --scrape-only to create databases first.")
                return

            # Step 4: Scrape and populate data
            print("\n" + "=" * 60)
            scrape_stats = scrape_and_populate_all_countries(country_to_database, max_workers=2)

            # Final Summary
            elapsed_time = time.time() - start_time
            print("\n" + "=" * 60)
            print("Final Summary:")
            print(f"  Countries with databases: {len(country_to_region)}")
            print(f"  Countries scraped: {scrape_stats.get('countries_processed', 0)}")
            print(f"  Total companies found: {scrape_stats.get('total_companies_found', 0)}")
            print(f"  Total companies added: {scrape_stats.get('total_companies_added', 0)}")
            print(f"  Errors: {scrape_stats.get('errors', 0)}")
            print(f"  Total time: {elapsed_time:.2f} seconds")
            print("=" * 60)
        else:
            print("[ERROR] NOTION_TOKEN and MAIN_PAGE_ID must be set in .env file")
    else:
        # Summary without scraping
        elapsed_time = time.time() - start_time
        print("\n" + "=" * 60)
        print("Summary:")
        print(f"  Countries processed: {len(country_to_region)}")
        print(f"  Notion databases created/verified")
        print(f"  Total time: {elapsed_time:.2f} seconds")
        print("=" * 60)


if __name__ == "__main__":
    main()
