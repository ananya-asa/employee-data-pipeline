# Employee Data Scraper

A Python project that scrapes employee data from a JSON API, validates its structure, and normalizes it based on specific business rules.

## Features
- **Robust Fetching**: Automatically retries on network timeouts.
- **Data Normalization**: Re-formats dates, merges names, and classifies job titles based on experience.
- **Data Validation**: Enforces strict data types across columns.

## Setup & Installation

1. Make sure Python is installed on your system.
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

To run the scraper and fetch the data:
```bash
python scraper.py
```
*This will fetch the data and output the clean, normalized results to `employees_normalized.csv`.*

## Running the Tests

To verify that the scraping logic and data transformations work correctly, run the automated unit test suite:
```bash
python -m unittest test_scraper.py
```

## Data Output Schema

The output file `employees_normalized.csv` will contain the following structured schema:

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| **Full Name** | `string` | Concatenation of `first_name` and `last_name`. |
| **email** | `string` | The employee's contact email address. |
| **phone** | `integer/string` | Filtered numerical phone, or `"Invalid Number"` if it contained 'x'. |
| **gender** | `string` | Employee's gender designation. |
| **age** | `integer` | Employee age. |
| **job_title** | `string` | The provided job title. |
| **years_of_experience**| `integer` | The total number of years of experience. |
| **salary** | `integer` | Base salary amount. |
| **department**| `string` | Department assignment. |
| **designation** | `string` | Derived field: `system engineer` (<3 yrs), `data engineer` (3-4 yrs), `senior data engineer` (5-10 yrs), or `lead` (>10 yrs). |
| **hire_date** | `string` | Normalized to `YYYY-MM-DD` standard format. |
