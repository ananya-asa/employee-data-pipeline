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
