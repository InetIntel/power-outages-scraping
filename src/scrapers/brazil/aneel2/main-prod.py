import sys
import argparse
import json
from datetime import datetime

# Note: These files must be accessible in the Docker image's PATH
from Scraper import Scraper
from utils import StorageClient

# --- Configuration ---
BUCKET_NAME = "" # Must match the bucket name in S3Client

def main():
    parser = argparse.ArgumentParser(description="Aneel Scraper and Processor DAG Step.")
    
    # Common arguments for step dispatch
    parser.add_argument('--step', required=True, choices=['scrape', 'process'],
                        help="The DAG step to execute: 'scrape' or 'process'.")
    
    # Specific argument for the 'process' step (the S3 Key passed from DAGU)
    parser.add_argument('--s3-key', type=str,
                        help="The S3 key of the raw file to process.")
    
    args = parser.parse_args()
    try:
        # Run either the scrape or process step
        output_key, output_val = None, None
        if args.step == 'scrape':
            BUCKET_NAME = "raw"
            year = args.year if year in args else None
            scraper = Scraper(year=year) 

            # --- Dispatch to Aneel.scrape() ---
            # Assume Scraper.scrape() returns the full S3 key (e.g., 'raw/2024/data.csv')
            output_key = 's3_file_key'
            output_val = scraper.scrape()
        elif args.step == 'process':
            if not args.s3_file_key:
                raise ValueError("The 'process' step requires the '--s3-key' argument from the previous step.")
            
            BUCKET_NAME = "processed"
            year = args.year if year in args else None
            scraper = Scraper(year=year) 

            # output_key = '' # not necesssary 
            # output_val = scraper.process(raw_s3_key=args.s3_key)

        # Output the file name to stdout for usage by later steps
        # -- technically only useful for `process` to access `scrape`'s files but w/e
        if output_key and output_val:
            output_data = {output_key: output_val}
            # Print the single JSON line to STDOUT for DAGU to capture
            print(json.dumps(output_data))
            
    except Exception as e:
        # Print errors to STDERR and exit non-zero for reliable DAGU step failure
        print(f"FATAL ERROR in {args.step} step: {e}", file=sys.stderr)
        sys.exit(1) # sys.exit -> can return later

if __name__ == "__main__":
    main()