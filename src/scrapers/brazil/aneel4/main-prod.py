import traceback
import sys
import argparse
import json
from datetime import datetime
import os
from Scraper import Scraper
from utils import parse_time_delta_string

def main():
    parser = argparse.ArgumentParser(description="Aneel Scraper and Processor DAG Step.")
    
    # CLI arguments for step dispatch
    parser.add_argument('--step', required=True, choices=['scrape', 'process', 'scrape_upload', 'download_process_upload'],
                        help="The DAG step to execute: 'scrape' or 'process'.")
    
    parser.add_argument('--time_delta', type=str, default='24h',
                        help="Time window for processing (e.g., '1h', '3d', '1w').")

    args = parser.parse_args()
    try:
        # local testing w/o docker: below two doesn't really do much. likely errs outs
        if args.step == 'scrape_upload':
            scraper = Scraper() 
            scraper.scrape_upload()
        elif args.step == 'download_process_upload':
            scraper = Scraper() 
            time_delta = parse_time_delta_string(args.time_delta)
            scraper.download_process_upload(time_delta=time_delta)

        # use below two to test scrape and process in isolation.
        elif args.step == 'scrape':
            scraper = Scraper() 
            scraper.scrape()
        elif args.step == 'process':
            scraper = Scraper() 
            scraper.process()
        else:
            raise ValueError("Invalid DAG step provided")

    except Exception as e:
        # Print errors to STDERR and exit non-zero for reliable DAGU step failure
        print(f"[main_prod] Error in {args.step} step: {e}")
        traceback.print_exc() 
        sys.exit(1) # sys.exit -> can return later

if __name__ == "__main__":
    main()