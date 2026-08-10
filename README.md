# Employee Data Pipeline

A Python project that scrapes employee data from JSON APIs, Google Drive files, and ZIP archives containing Excel data, validates data structures, and normalizes employee records for ingestion into data warehouses.

## Features
- **JSON API Scraper (`scraper.py`)**: Fetches employee JSON data, normalizes dates, merges full names, formats phone numbers, and assigns designations based on experience.
- **Google Drive File Scraper (`gdrive_scraper.py`)**: Scrapes employee data from Google Drive URLs (CSV/Excel files), validates required data structures, and normalizes employee fields.
- **ZIP File Scraper (`zip_scraper.py`)**: Downloads and extracts employee data from ZIP file URLs, selects and parses Excel data files (`.xlsx`), validates file integrity & schemas, splits names, formats dates, and normalizes employee records.
- **Robust Network & Retry Logic**: Gracefully handles network timeouts and retries failed downloads.
- **Data Validation & Type Enforcement**: Verifies required schemas and enforces standard data types.

## Setup & Installation

1. Make sure Python is installed on your system.
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### User Story 1: Scraping Employee Data from API
```bash
python scraper.py
```
*Outputs clean, normalized results to `employees_normalized.csv`.*

### User Story 2: Scraping Employee Data from Google Drive File
```bash
python gdrive_scraper.py
```
*Downloads the employee CSV/Excel file from Google Drive and outputs normalized records to `gdrive_employees_normalized.csv`.*

### User Story 3: Scraping Employee Data from ZIP File
```bash
python zip_scraper.py
```
*Downloads and extracts the employee ZIP file, parses the Excel sheet (`.xlsx`), and outputs normalized records to `zip_employees_normalized.csv`.*

## Running the Tests

To verify that the scraping logic and data transformations work correctly across all user stories:

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

## Data Output Schema (ZIP Scraper)

The output file `zip_employees_normalized.csv` contains the mapped schema:

| Standard Field | Mapped From | Description |
|----------------|-------------|-------------|
| **Employee ID** | `EEID` / `User Id` | Unique identifier for employee |
| **First Name** | `First Name` / `Full Name` (split) | Employee first name |
| **Last Name** | `Last Name` / `Full Name` (split) | Employee last name |
| **Email** | `Email` | Employee email address |
| **Job Title** | `Job Title` | Position title |
| **Phone Number** | `Phone` / `Phone Number` | Phone contact number |
| **Hire Date** | `Hire Date` / `Date of birth` | Date string formatted to `YYYY-MM-DD` |

