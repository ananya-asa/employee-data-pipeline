# Employee Data Pipeline

A Python project that scrapes employee data from JSON APIs and Google Drive files, validates data structures, and normalizes employee records for ingestion into data warehouses.

## Features
- **JSON API Scraper (`scraper.py`)**: Fetches employee JSON data, normalizes dates, merges full names, formats phone numbers, and assigns designations based on experience.
- **Google Drive File Scraper (`gdrive_scraper.py`)**: Scrapes employee data from Google Drive URLs (CSV/Excel files), validates required data structures, and normalizes employee fields.
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

## Running the Tests

To verify that the scraping logic and data transformations work correctly across both user stories:

### User Story 1 Tests (API Scraper):
```bash
python -m unittest test_scraper.py
```

### User Story 2 Tests (Google Drive Scraper):
```bash
python -m unittest test_gdrive_scraper.py
```

## Data Output Schema (Google Drive Scraper)

The output file `gdrive_employees_normalized.csv` contains the mapped schema:

| Standard Field | Mapped From | Description |
|----------------|-------------|-------------|
| **Employee ID** | `User Id` | Unique identifier for employee |
| **First Name** | `First Name` | Employee first name |
| **Last Name** | `Last Name` | Employee last name |
| **Email** | `Email` | Employee email address |
| **Job Title** | `Job Title` | Position title |
| **Phone Number** | `Phone` | Phone contact number |
| **Hire Date** | `Date of birth` / `Hire Date` | Date string in `YYYY-MM-DD` standard format |
