import os
import sys
import shutil
from pathlib import Path

TEMPLATES_DIR = Path("templates/scraper")
BASE_SCRAPERS_DIR = Path("src/scrapers")
DAGU_TEMPLATE_FILE = Path("templates/DAGU_config_template.yaml")

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
    code_dest_dir = BASE_SCRAPERS_DIR / country_name / section_name

    yaml_filename = f"{country_name}_{section_name}.yaml"
    yaml_dest_path = Path(f"./dagu_config/dags/{yaml_filename}")
    
    # Check if the distination dirs already exist
    if code_dest_dir.exists():
        print(f"\n[ERROR] Destination directory already exists: {code_dest_dir}. Aborting.", file=sys.stderr)
        sys.exit(1)
    if yaml_dest_path.exists():
        print(f"\n[ERROR] Destination directory already exists: {code_dest_dir}. Aborting.", file=sys.stderr)
        sys.exit(1)

    # Copying the scraper files
    try:
        print(f"\n[INFO] Creating new scraper directory structure...")
    
        shutil.copytree(TEMPLATES_DIR, code_dest_dir) # copies src dir into dest dir and creates dirs as needed.
    
        print(f"[SUCCESS] Directory created: {code_dest_dir}")
        print(f"[SUCCESS] Template files copied from {TEMPLATES_DIR}.")
    except FileNotFoundError:
        print(f"\n[ERROR] Template directory not found: {TEMPLATES_DIR}. Please check the path.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] An error occurred during file copying: {e}")
        sys.exit(1)

    # copying and editing the DAGU YAML
    try:
        print(f"[INFO] Generating DAGU config file: {yaml_dest_path}")
        
        template_content = DAGU_TEMPLATE_FILE.read_text()
        scraper_name_for_image = f"{country_name}_{section_name}" 
        
        # there are a couple placeholder `@replace_scraper_name` vars inside the template
        replaced_content = template_content.replace(
            "@replace_scraper_name", scraper_name_for_image
        )

        yaml_dest_path.write_text(replaced_content)
        print(f"[SUCCESS] DAGU config saved to {yaml_dest_path}")
    except Exception as e:
        print(f"\n[FATAL] An error occurred during YAML generation: {e}", file=sys.stderr)
        # You might want to clean up the partially created code_dest_dir here if necessary
        sys.exit(1)

    print("\n[SUCCESS] New scraper successfully initialized!")


if __name__ == "__main__":
    config = get_user_input()
    create_scraper_project(config)