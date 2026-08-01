import requests
import time
import pandas as pd
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_data(url: str, retries: int = 3) -> list:
    """Fetches data from the given URL with simple retry logic."""
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt == retries - 1:
                logging.error("Max retries reached. Failing.")
                raise
            time.sleep(1) # wait 1 second before retrying

def assign_designation(exp: int) -> str:
    """Assign designation based on years of experience."""
    if pd.isna(exp):
        return None
    if exp < 3:
        return 'system engineer'
    elif 3 <= exp < 5:
        return 'data engineer'
    elif 5 <= exp <= 10:
        return 'senior data engineer'
    else:
        return 'lead'

def parse_phone(phone_val) -> object:
    """Process phone string."""
    if pd.isna(phone_val):
        return phone_val
    val_str = str(phone_val).lower()
    if 'x' in val_str:
        return "Invalid Number"
    # Keep only digits
    digits = re.sub(r'\D', '', val_str)
    if digits:
        return int(digits)
    return "Invalid Number"

def normalize_data(raw_data: list) -> pd.DataFrame:
    """Validates and normalizes raw employee data."""
    if not raw_data:
        return pd.DataFrame()

    df = pd.DataFrame(raw_data)

    # 2. Combine first_name and last_name into Full Name
    if 'first_name' in df.columns and 'last_name' in df.columns:
        df['Full Name'] = df['first_name'] + ' ' + df['last_name']
    else:
        df['Full Name'] = None
        
    # 1. Create designation based on years_of_experience
    if 'years_of_experience' in df.columns:
        # ensure it's numeric first
        df['years_of_experience'] = pd.to_numeric(df['years_of_experience'], errors='coerce')
        df['designation'] = df['years_of_experience'].apply(assign_designation)
    
    # 3. Phone logic
    if 'phone' in df.columns:
        df['phone'] = df['phone'].apply(parse_phone)

    # 6. Date Formatting if available
    for date_col in ['hire_date', 'Hire Date']:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce').dt.strftime('%Y-%m-%d')

    # 4. Enforce Data Types
    type_mapping = {
        'Full Name': 'string',
        'email': 'string',
        'gender': 'string',
        'age': 'Int64', # nullable int
        'job_title': 'string',
        'years_of_experience': 'Int64',
        'salary': 'Int64',
        'department': 'string'
    }
    
    for col, dtype in type_mapping.items():
        if col in df.columns:
            if dtype == 'string':
                df[col] = df[col].astype(str)
                # handle 'nan' string from conversion
                df[col] = df[col].replace('nan', pd.NA)
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype(dtype)

    return df

def main():
    url = "https://api.slingacademy.com/v1/sample-data/files/employees.json"
    try:
        logging.info("Fetching data...")
        data = fetch_data(url)
        logging.info("Normalizing data...")
        df = normalize_data(data)
        logging.info("Data processing complete.")
        
        # Save to csv for inspection
        df.to_csv("employees_normalized.csv", index=False)
        logging.info("Saved normalized data to employees_normalized.csv")
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")

if __name__ == "__main__":
    main()
