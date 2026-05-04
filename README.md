# Amazon Bestseller lists: scraping
This project is meant to scrape the page of Amazon fiction charts, found here: https://www.amazon.com/charts/2026-04-26/mostsold/fiction?

## Running the scraper
The extract_data.py file contains the key data extraction functions. This is where you can write in your API key.

The run_scraper_wproxy.py file is the file you must run to actually run the scraper. This can be done by either creating a new CSV or appending to an existing one (read comments in file). These are the only two files needed to run the scraper.

Please note this program will take a long time given the API dependency and sleep times. Plan accordingly.

## Dependencies
BeautifulSoup, a Scraper API key, and Python are required for this project. While this can be done incrementally on a free API service, buying one with more capacity is strongly recommended.

If you use ScraperAPI, the project can be completed with the basic paid level, under 100,000 tokens.

## Use
If you use this for a project, please give credit by linking back to this repository.
