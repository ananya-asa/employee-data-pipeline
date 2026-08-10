# Data Scraping Pipelines

This repository contains multiple data scraping projects for extracting, validating, and normalizing data from various sources (Websites, JSON APIs, Google Drive files, ZIP archives).

## Features

- **Books Web Scraper (`book_scraper.py`)**: Scrapes book details (Title, Price, Rating, Availability, URL) from `books.toscrape.com`, automatically handling pagination across all pages (up to 1000 books). Gracefully handles missing data and network timeouts, exporting results to a structured CSV.
- **JSON API Scraper (`scraper.py`)**: Fetches employee JSON data, normalizes dates, merges full names, formats phone numbers, and assigns designations based on experience.
- **Google Drive File Scraper (`gdrive_scraper.py`)**: Scrapes employee data from Google Drive URLs (CSV/Excel files), validates required data structures, and normalizes employee fields.
- **ZIP File Scraper (`zip_scraper.py`)**: Downloads and extracts employee data from ZIP file URLs, selects and parses Excel data files (`.xlsx`), validates file integrity & schemas, splits names, formats dates, and normalizes employee records.
- **Robust Network & Retry Logic**: Gracefully handles network timeouts, HTTP errors, and retries failed downloads.

## Setup & Installation

1. Ensure Python 3 is installed.
2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
```
3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

*(Note: If using `book_scraper.py`, you will also need to install `beautifulsoup4` and `requests`. Tests require Python's built-in `unittest`)*

## Usage

### User Story: Books Web Scraper
**Business Flow:**
1. Connects to `books.toscrape.com` and downloads the HTML.
2. Extracts book attributes (Title, Price, 1-5 Rating, Availability, URL).
3. Follows pagination links to scrape all subsequent pages automatically.
4. Skips gracefully if essential attributes are missing or HTTP errors occur.
5. Saves all extracted book data to a CSV file.

**Command:**
```bash
python book_scraper.py
```
*Outputs structured book details to `books_data.csv`.*

### User Story: Scraping Employee Data from API
```bash
python scraper.py
```
*Outputs clean, normalized results to `employees_normalized.csv`.*

### User Story: Scraping Employee Data from Google Drive File
```bash
python gdrive_scraper.py
```
*Downloads the employee CSV/Excel file from Google Drive and outputs normalized records to `gdrive_employees_normalized.csv`.*

### User Story: Scraping Employee Data from ZIP File
```bash
python zip_scraper.py
```
*Downloads and extracts the employee ZIP file, parses the Excel sheet (`.xlsx`), and outputs normalized records to `zip_employees_normalized.csv`.*

## Running the Tests

To verify that the scraping logic and data transformations work correctly across all user stories:

### Books Web Scraper Tests:
```bash
python test_book_scraper.py
```

### User Story 1 Tests (API Scraper):
```bash
python -m unittest test_scraper.py
```

### User Story 2 Tests (Google Drive Scraper):
```bash
python -m unittest test_gdrive_scraper.py
```

### User Story 3 Tests (ZIP File Scraper):
```bash
python -m unittest test_zip_scraper.py
```

### Run All Project Tests:
```bash
python -m unittest discover -p "test_*.py"
```
