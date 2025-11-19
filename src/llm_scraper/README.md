# LLM Company Scraper

This Jupyter notebook (`llm_company_scraper.ipynb`) implements an automated workflow for collecting power company data from various countries and storing it in Notion databases.

## Overview

The notebook performs the following main tasks:

1. **Fetch Country and Region Data** - Retrieves country and region information from the IODA API
2. **Create Notion Databases** - Sets up Notion databases for each country
3. **Generate Scraping Prompts** - Creates AI prompts for web scraping power company data
4. **Execute AI Scraping** - Uses OpenAI API to gather company information
5. **Update Notion Tables** - Stores the scraped data in the appropriate Notion databases

## Prerequisites

### Environment Variables
Set these in your environment or `.env` file:
- `NOTION_TOKEN` - Your Notion integration token
- `MAIN_PAGE_ID` - ID of the Notion page that will contain country databases
- `OPENAI_KEY` - Your OpenAI API key

### Python Packages
```bash
pip install requests notion-client openai python-dotenv
```

## Notebook Structure

### Cell 1: Fetch Country and Region Data
- Connects to IODA API (`https://api.ioda.inetintel.cc.gatech.edu/v2/entities/query`)
- Fetches all countries and their regions
- Uses concurrent processing with ThreadPoolExecutor for efficiency
- Stores results in `country_to_region` dictionary

### Cell 2: Create Notion Databases
- Initializes Notion client using environment variables
- Retrieves existing databases on the main page
- Creates new child databases for each country if they don't exist
- Database schema includes fields for company data, scraping info, and status

### Cell 3: Generate Scraping Prompts
- Defines `build_prompt(country)` function
- Creates detailed AI prompts for scraping power company data
- Prompts include specific JSON format requirements
- Instructions for handling non-English websites and comprehensive data collection

### Cell 4: Execute AI Scraping
- Uses OpenAI API with web search tools
- Processes each country from `country_to_region`
- Extracts JSON data from AI responses
- Handles API responses and JSON parsing

### Cell 5: Update Notion Tables
- Connects to specific country databases
- Checks for duplicate entries before insertion
- Maps scraped data to Notion database fields
- Handles multi-select fields and data type parsing

## Data Flow

```
IODA API → Country/Region Data
    ↓
Notion Database Creation
    ↓
AI Prompt Generation → OpenAI API → Scraped Company Data
    ↓
Notion Database Updates
```

## Key Features

### Concurrent Processing
- Uses ThreadPoolExecutor for API calls and database operations
- Improves performance when processing multiple countries

### Duplicate Prevention
- Checks for existing entries before creating new ones
- Uses company name and region for uniqueness

### Flexible Data Mapping
- Handles variations in field names across different data sources
- Supports multi-select fields for challenges, data types, etc.

### Error Handling
- Graceful handling of API failures
- Continues processing even if individual countries fail

## Output Schema

Each company record includes:
- **Company / Data source**: Company name
- **Region**: Geographic area served
- **Description**: Available outage data information
- **Comments on Web Scraping**: Manual scraping instructions
- **Power Outage Link**: Direct link to outage data
- **Website**: Company homepage
- **Official Government Website URL**: Source of company information
- **Scraping code created**: Status of automation development
- **Challenges**: Technical difficulties encountered
- **Data Type**: Available data formats (Future/Historical/Excel/None)
- **Scraping Frequency**: Data update frequency
- **Status**: Current scraping status

## Usage

1. Set up environment variables
2. Install required packages
3. Run cells in order (1→2→3→4→5)
4. Monitor output for any errors or skipped entries

## Notes

- The notebook is designed to run in Google Colab but can be adapted for local execution
- API rate limits may apply - consider adding delays between requests
- Some countries may have limited or no public power company data
- The scraping prompts are optimized for comprehensive data collection

## Troubleshooting

### Common Issues:
- **Notion API errors**: Check token permissions and page access
- **OpenAI API errors**: Verify API key and usage limits
- **IODA API errors**: Check network connectivity
- **JSON parsing errors**: AI responses may need manual review
