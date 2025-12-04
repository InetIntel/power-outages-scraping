## Data Retrieved

The pdfs retrieved and parsed by this scraper only contain data for upcoming planned outages. 
Each individual outage contans the following:

Municipo - (English: municipality), string containing areas affected by the outage. if there are multiple areas then 
they are separated by " | ".

Fecha - (English: date), string of current date.
(Example: "04/12/2025")

Hora Inicio - (English: start time), string, local time when outage began. (Example: "09:30")

Hora Fin - (English: end time), string, local time when outage is scheduled to end. (Example: "09:30")

## Data Retrieval

Code Process

scrape.py:

This script uses selenium to create a headless chrome browser. It's headless because it seemed like it needed to be in 
order to work properly in the docker container (not sure exactly why). However, in headless mode certain elements of 
the webpage were not accessible, so it is created with parameters to "fool" the webpage into thinking it is not 
headless. 

Once the broswer is started, it navigates to the iberdrola outage page which contains links to the different regions. 
From this page the scraper is able to collect the names of all the regions that are listed as well as the links to 
their pages. Once the scraper has this list created, it then navigates to the webpages for all the individual regions 
covered by the provider. From each of these region specific pages, the scraper collects the download link for the 
pdf file containing all the planned outages in that region for the week. Once this is completed, the scraper now 
has a list of download links to all the pdf files with the planned outage data. 

Next the scraper iterates through the list of pdf download links, downloading them one at a time. For each download, it 
waits until the download is finished by detecting new files in the download directory. It then renames each file to 
contian the current date (day, month, year). Then it iterates through all these files and uploads them to minio for 
storage. While uploading, it skips files with names containing "SGS", these are occasional stray file downloads, I'm 
not sure why that's happening.

post_process.py:

**download_raw_pdfs() function still needs to be finished. The minio download functionality wasn't working yet when this 
script was written.

This script downloads from minio the pdfs that were collected by scrape.py, parses out the data that is needed, 
saves the data in a json, then uploads the json to minio. 

For pdf parsing, I used pdfplumber. The core parsing logic uses regular expressions to identify the rows of the outage 
table, which contain a municipality name, date, start time, end time, and optionally an address. As it reads each line, 
the script builds outage records, appending wrapped address lines where needed (identified via common Spanish street 
prefixes). It also extracts the province name from the first few lines of the PDF. The parsed records are assembled 
into a pandas DataFrame, with dates and times converted to proper Python datetime objects. The parse_folder function 
then applies this logic to every PDF in a directory, combining all results into one DataFrame.

Once parsed, df_to_json converts the DataFrame into a list of clean outage records, computing full start/end timestamps 
and the duration in hours. The address data is currently flattened into municipal-level “areas_affected” entries because 
many PDFs contain inconsistent street formatting. The JSON output is saved alongside the script, with a timestamped 
filename for traceability. The script also includes an upload() function that sends processed JSON files to MinIO 
storage.


## Other Notes

The dataset updates weekly.

Data only includes planned outages.

Outage data is in local timezone, NEEDS TO BE UPDATED TO UTC.

post_process.py currently isn't working because it is assuming the pdfs that need to be parsed are already stored in 
local docker container. At the time this script was written the minio download functionality wasn't finished, so the 
download_raw_pdfs() function needs to be updated to download the pdfs containing the raw data from minio to container.