# Japan Power Outage Scrapers

This group of folders are the collection of scrapers for storing and processing power outage data from power companies across Japan.

## Overview
Each of these scrapers aims to collect the outage data from a past outages table for each respective company. Every folder for each power company contains at least the following files:

1. **Scrape.py** - Responsible for fetching raw data from the past outage tables, either using the company's endpoints for a group of XML, CSV, or JSON files. If not available, the website's HTML is saved to be processed. Regardless, it will store these files under:
    ```bash
    <company>/data/raw
    ```

2. **Post_Process.py** - Reads the raw files and converts them into a standardized JSON structure. It will then store these files under:
    ```bash
    <company>/data/processed
    ```


## Usage

### 1. Run scrape.py
If running a terminal under the path scrapers/japan and downloading the required dependencies, run:

    python <company_name>/scrape.py

If successful, you should see the folder under the path stated in the overview populated with files.

### 2. Run post_process.py
Make sure that the data/raw folder is populated with the corresponding HTML/JSON/XML files, then run:

    python <company_name>/post_process.py

If successful, you should see the processed JSON in the folder under the path stated in the overview.

## Output Format
Though the format may vary slightly depending on the table for each website scraped from, here are the general details:

- **Start**: The start time for a power outage.
- **End**: The end time for a power outage.
- **Area**: The area where the outage occurred in. Details depend on the table scraped from, but the prefecture should always be included, sometimes along with cities & towns.
- **Households Affected**: The number of household affected by the power outage, sometimes blank if under investigation or unknown at current time.
- **Reason**: The reason the power outage occurred, also may be blank if under investigation.

## Notes
- These scrapers are designed at the moment to be ran locally, however tohoku has extra files to run with DAGU. Run tohoku.py then tohoku_process.py to run locally.
- Often times it would be best to delete data in the raw folder before running post_process.py as it may try to process duplicate instances for the same outage.
- All scrapers are designed to scrape data for the past week, but Tokyo(TEPCO) and Tohoku should have data for the past two months and one month respectively.
- Kyushu's scrape.py is unique as it scrapes a group of CSV files 40-46 that appear to align with ISO codes for Japan. You will most likely get varied numbers of responses(resultant files) depending on which areas had outages or not.


    
