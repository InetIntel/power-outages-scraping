# Developer Notes

## Data Source  
The scraper pulls data from the following website:  
**"https://nesco.portal.gov.bd/site/view/miscellaneous_info/%E0%A6%AC%E0%A6%BF%E0%A6%A6%E0%A7%8D%E0%A6%AF%E0%A7%81%E0%A7%8E-%E0%A6%AC%E0%A6%A8%E0%A7%8D%E0%A6%A7%E0%A7%87%E0%A6%B0-%E0%A6%AC%E0%A6%BF%E0%A6%9C%E0%A7%8D%E0%A6%9E%E0%A6%AA%E0%A7%8D%E0%A6%A4%E0%A6%BF"**

## Website Language & Translation
The website content is in **Bengali (Bangla)**.  
There is an English translation button on the top-right of the page.  
Originally, the scraper used the `translate()` function in `scrape.py` to click the button and switch the site to English.

However:

- The translation button is often broken or unresponsive.
- Because of this, the translation click feature is now disabled.
- Data is scraped in **Bengali**, and translation is done afterward using LLMs.

## Chrome Installation (Required Before Running `scrape.py`)
Before executing `scrape.py`, install Google Chrome:

```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```

## Scraping Frequency & Improvement Needed
The website updates its records **weekly**, so scraping once per week is enough.

Current scraper behavior:

- `scrape.py` always fetches the **latest 100 records**.
- This means it repeatedly downloads already-scraped data.

**Future improvement needed:**  
✔ Only scrape **new, unrecorded** entries.

## Post-Processing & API Cost
`post_process.py` uses the **OpenAI API** to translate data and extract structured information.

Notes:

- The API is **not free**.
- You must provide a valid `API_KEY` before running the script.
