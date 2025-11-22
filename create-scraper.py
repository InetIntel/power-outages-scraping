import os
import sys
import shutil
from pathlib import Path

# --- Configuration ---
TEMPLATES_DIR = Path("templates/scraper")
BASE_SCRAPERS_DIR = Path("src/scrapers")

def get_user_input() -> dict:
    """
    Prompts user for required configuration details.
    """
    print("\n--- Scraper Project Initializer ---")
    
    country = input("1. Enter Country Name (e.g., brazil): ").strip().lower()
    section = input("2. Enter Power Company/Section Name (e.g., aneel): ").strip().lower()

    if not country or not section:
        print("\n[ERROR] Both fields are required. Aborting.", file=sys.stderr)
        sys.exit(1)

    return {
        "country": country,
        "section": section,
    }

def create_scraper_project(config: dict):
    """
    Copies template files and creates the destination directory structure.
    """
    country_name = config["country"]
    section_name = config["section"]
    
    # Define destination path: src/scrapers/given_country/given_2ndary_sectional
    dest_dir = BASE_SCRAPERS_DIR / country_name / section_name
    
    # Check if the destination already exists
    if dest_dir.exists():
        print(f"\n[ERROR] Directory already exists: {dest_dir}. Aborting.", file=sys.stderr)
        sys.exit(1)

    print(f"\n[INFO] Creating new scraper directory structure...")
    
    # --- 1. Copy Template Directory ---
    try:
        shutil.copytree(TEMPLATES_DIR, dest_dir) # copies src dir into dest dir and creates dirs as needed.
        print(f"[SUCCESS] Directory created: {dest_dir}")
        print(f"[SUCCESS] Template files copied from {TEMPLATES_DIR}.")
    except FileNotFoundError:
        print(f"\n[FATAL] Template directory not found: {TEMPLATES_DIR}. Please check the path.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FATAL] An error occurred during file copying: {e}")
        sys.exit(1)

    print("\n[INFO] Next step: Implement logic and run the build script.")


if __name__ == "__main__":
    try:
        config = get_user_input()
        create_scraper_project(config)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)