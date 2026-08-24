# Data Scraping Pipelines

This repository contains multiple data scraping projects for extracting, validating, and normalizing data from various sources (Websites, JSON APIs, Google Drive files, ZIP archives, and Power BI reports).

## Repository Structure

The project is structured into modular user story directories:
- **[`user_story_1_api_scraper/`](file:///d:/Internship/user_story_1_api_scraper/)**: Fetches employee JSON data, normalizes dates, merges full names, formats phone numbers, and assigns designations.
- **[`user_story_2_gdrive_scraper/`](file:///d:/Internship/user_story_2_gdrive_scraper/)**: Scrapes employee data from Google Drive URLs (CSV/Excel files), validates required data structures, and normalizes employee fields.
- **[`user_story_3_zip_scraper/`](file:///d:/Internship/user_story_3_zip_scraper/)**: Downloads and extracts employee data from ZIP file URLs, selects and parses Excel data files (`.xlsx`), validates file integrity, splits names, formats dates, and normalizes employee records.
- **[`user_story_4_book_scraper/`](file:///d:/Internship/user_story_4_book_scraper/)**: Scrapes book details (Title, Price, Rating, Availability, URL) from `books.toscrape.com`, automatically handling pagination across all pages (up to 1000 books).
- **[`user_story_5_power_bi/`](file:///d:/Internship/user_story_5_power_bi/)**: Contains report design guidelines, M query, DAX functions, and an automated verification test suite to validate data cleaning and KPIs.

---

## Setup & Installation

1. Ensure Python 3 is installed.
2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv .venv
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
```
3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

*(Note: If using book scrapers, you will also need to install `beautifulsoup4` and `requests`. Tests require Python's built-in `unittest`)*

---

## Usage

### User Story 4: Books Web Scraper
**Business Flow:**
1. Connects to `books.toscrape.com` and downloads the HTML.
2. Extracts book attributes (Title, Price, 1-5 Rating, Availability, URL).
3. Follows pagination links to scrape all subsequent pages automatically.
4. Saves all extracted book data to a CSV file.

**Command:**
```bash
python user_story_4_book_scraper/book_scraper.py
```
*Outputs structured book details to `user_story_4_book_scraper/books_data.csv`.*

### User Story 1: Scraping Employee Data from API
```bash
python user_story_1_api_scraper/scraper.py
```
*Outputs clean, normalized results to `user_story_1_api_scraper/employees_normalized.csv`.*

### User Story 2: Scraping Employee Data from Google Drive File
```bash
python user_story_2_gdrive_scraper/gdrive_scraper.py
```
*Downloads the employee CSV/Excel file from Google Drive and outputs normalized records to `user_story_2_gdrive_scraper/gdrive_employees_normalized.csv`.*

### User Story 3: Scraping Employee Data from ZIP File
```bash
python user_story_3_zip_scraper/zip_scraper.py
```
*Downloads and extracts the employee ZIP file, parses the Excel sheet, and outputs normalized records to `user_story_3_zip_scraper/zip_employees_normalized.csv`.*

---

## Running the Tests

To verify that the scraping logic and data transformations work correctly across all user stories:

### User Story 1 Tests (API Scraper):
```bash
python user_story_1_api_scraper/test_scraper.py
```

### User Story 2 Tests (Google Drive Scraper):
```bash
python user_story_2_gdrive_scraper/test_gdrive_scraper.py
```

### User Story 3 Tests (ZIP File Scraper):
```bash
python user_story_3_zip_scraper/test_zip_scraper.py
```

### User Story 4 Tests (Books Web Scraper):
```bash
python user_story_4_book_scraper/test_book_scraper.py
```

### User Story 5 Tests (Power BI Dashboard Validation):
```bash
python user_story_5_power_bi/test_dashboard.py
```

### Run All Project Tests:
```bash
python -m unittest discover -s . -p "test_*.py"
```
