import traceback
import sys
import argparse
import json
from datetime import datetime
import os
from Scraper import Scraper
# from utils import StorageClient

def main():
    parser = argparse.ArgumentParser(description="Aneel Scraper and Processor DAG Step.")
    
    # CLI arguments for step dispatch
    parser.add_argument('--step', required=True, choices=['scrape', 'upload_raw', 'process', 'upload_processed'],
                        help="The DAG step to execute: 'scrape' or 'process'.")
    
    args = parser.parse_args()
    try:
        # Run either the scrape or process step
        if args.step == 'scrape':
            scraper = Scraper() 
            scraper.scrape()
        elif args.step == 'upload_raw':
            scraper = Scraper() 
            scraper.upload_raw()
        elif args.step == 'process':
            scraper = Scraper() 
            scraper.process()
        elif args.step == 'upload_processed':
            scraper = Scraper() 
            scraper.upload_processed()
        else:
            raise ValueError("Invalid DAG step provided")

    except Exception as e:
        # Print errors to STDERR and exit non-zero for reliable DAGU step failure
        print(f"[main_prod] Error in {args.step} step: {e}")
        traceback.print_exc() 
        sys.exit(1) # sys.exit -> can return later

if __name__ == "__main__":
    main()