# Power Outage Data Scraping Code

#### This repository contains the code to craw power outage data.

### The structure is as below:

#### 1. Data Analysis Directory

##### This directory contains raw csv data about Internet outages from `KeepItOn` and the analysis of the data. We order the occurrences with the most occurrences to the least, and we prioritize the countries experienced more Internet outages, like India and Ukraine.

#### 2. {country name} Directory

##### The directories named with the country is the scraping code for the power information websites from this country. Every country is divided into different regions.

#### 3. {power provider} Directory

##### Each directory named with the power provider contains one Python file to scrape outage data from website and save the raw data, another Python file to process the saved raw data and save the processed data in desired format. The file name of a processor file contains "process" or "processor".

### How to run Python file

#### 1. Scraper file

##### Scraper files for each provider can be directly executed. For Scrapers in India, Nigeria, and Pakistan directories, processor will be called when running the scraper files.

#### 2. Processor file (India, Nigeria, Pakistan)

##### Referring to the processor file - process_npp.py in directory india/npp as example, first to provide a relative path to a `file` for processing. Then, modify the variable, `self.folder_path`, in function `check_folder`. This folder path is where you would like to save the processed file. Finally, run the python file.



