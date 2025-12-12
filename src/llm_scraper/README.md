# LLM Company Scraper

This project implements an automated workflow for collecting power company data from various countries and storing it in Notion databases using OpenAI's GPT models.

## Overview

The `main.py` script performs the following main tasks:

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
- `OPENAI_API_KEY` - Your OpenAI API key
- `WEB_SEARCH_MODEL` - GPT model for web scraping (default: gpt-4o-mini)
- `PARSING_MODEL` - GPT model for parsing JSON (default: gpt-4o-mini)

### Python Packages
```bash
pip install -r requirements.txt
```

## Model Configuration

Models are configurable at the beginning of `main.py`:

```python
WEB_SEARCH_MODEL = os.getenv('WEB_SEARCH_MODEL', 'gpt-4o-mini')
PARSING_MODEL = os.getenv('PARSING_MODEL', 'gpt-4o-mini')
```

**To use different models:**

```powershell
$env:WEB_SEARCH_MODEL="gpt-4o"
$env:PARSING_MODEL="gpt-4o-mini"
python main.py --scrape
```

## Usage

### Basic Usage

```bash
# Create databases for all countries (no scraping)
python main.py

# Create database for specific country
python main.py --country Brazil

# Create database AND scrape for specific country
python main.py --country Austria --scrape

# Scrape all countries (assumes databases exist)
python main.py --scrape

# Scrape without creating databases
python main.py --scrape-only

# Show help
python main.py --help
```

## Key Features

### Concurrent Processing
- Uses ThreadPoolExecutor for API calls and database operations
- Improves performance when processing multiple countries
- Configurable worker pool sizes

### Duplicate Prevention
- Checks for existing entries before creating new ones
- Uses company name and region for uniqueness

### Flexible Data Mapping
- Handles variations in field names across different data sources
- Supports multi-select fields for challenges, data types, etc.

### Error Handling
- Graceful handling of API failures
- Continues processing even if individual countries fail
- Detailed error logging with country context

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

## Workflow Examples

### Example 1: Setup for a New Country

```bash
python main.py --country Brazil
```

### Example 2: Scrape and Populate Data

```bash
python main.py --country India --scrape
```

### Example 3: Batch Process All Countries

```bash
python main.py --scrape
```

## Notes

- API rate limits may apply - consider adding delays between requests if processing many countries
- Some countries may have limited or no public power company data
- The scraping process depends on web availability and OpenAI API status

## Troubleshooting

### Common Issues:

**Notion API errors**
- Check that NOTION_TOKEN has proper permissions
- Verify MAIN_PAGE_ID exists and is accessible

**OpenAI API errors**
- Verify API key is valid in `.env` file
- Check account has sufficient credits/quota

**IODA API errors**
- Check network connectivity
- Try again if API is temporarily unavailable

**JSON parsing errors**
- Try using a more capable model (gpt-4o instead of gpt-4o-mini)
- Check that country name is spelled correctly