import os
import time
import logging
import requests
import pandas as pd

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

DEFAULT_URL = "https://drive.google.com/uc?id=1AWPf-pJodJKeHsARQK_RHiNsE8fjPCVK&export=download"

COLUMN_MAPPING = {
    "User Id": "Employee ID",
    "First Name": "First Name",
    "Last Name": "Last Name",
    "Email": "Email",
    "Phone": "Phone Number",
    "Date of birth": "Hire Date",
    "Job Title": "Job Title",
    "Employee ID": "Employee ID",
    "Phone Number": "Phone Number",
    "Hire Date": "Hire Date"
}

REQUIRED_COLUMNS = [
    "Employee ID",
    "First Name",
    "Last Name",
    "Email",
    "Job Title",
    "Phone Number",
    "Hire Date"
]

def download_file(url: str, output_path: str = None, retries: int = 3) -> str:
    """Download file from Google Drive URL with retry logic."""
    for attempt in range(retries):
        try:
            logging.info(f"Downloading file from URL... Attempt {attempt + 1}/{retries}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            if not output_path:
                content_type = response.headers.get("Content-Type", "").lower()
                content_disp = response.headers.get("Content-Disposition", "").lower()

                if "excel" in content_type or "sheet" in content_type or ".xlsx" in content_disp or ".xls" in content_disp:
                    output_path = "downloaded_employees.xlsx"
                else:
                    output_path = "downloaded_employees.csv"

            with open(output_path, "wb") as f:
                f.write(response.content)

            logging.info(f"File downloaded successfully as {output_path}")
            return output_path

        except requests.exceptions.RequestException as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt == retries - 1:
                logging.error("Maximum retry limit reached. File download failed.")
                raise
            time.sleep(1)

def identify_file_type(file_path: str) -> str:
    """Identify the file format (csv, excel, or unsupported)."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.csv', '.txt']:
        return 'csv'
    elif ext in ['.xlsx', '.xls']:
        return 'excel'

    try:
        with open(file_path, 'rb') as f:
            header = f.read(512)
            if header.startswith(b'PK') or b'xl/' in header:
                return 'excel'
            try:
                header_text = header.decode('utf-8', errors='ignore')
                if ',' in header_text or '\n' in header_text:
                    return 'csv'
            except Exception:
                pass
    except Exception as e:
        logging.error(f"Error inspecting file type: {e}")

    return 'unsupported'

def read_file(file_path: str) -> pd.DataFrame:
    """Read CSV or Excel file into a pandas DataFrame."""
    logging.info(f"Reading file: {file_path}")
    file_type = identify_file_type(file_path)

    try:
        if file_type == 'csv':
            df = pd.read_csv(file_path)
        elif file_type == 'excel':
            df = pd.read_excel(file_path)
        else:
            try:
                df = pd.read_csv(file_path)
            except Exception:
                logging.error(f"Invalid or unexpected file format for file: {file_path}")
                raise ValueError("Invalid or unexpected file format.")

        logging.info(f"File read successfully. Columns found: {list(df.columns)}")
        return df
    except ValueError:
        raise
    except Exception as e:
        logging.error(f"Failed to parse file: {e}")
        raise ValueError(f"Invalid or unexpected file format: {e}")

def validate_data(df: pd.DataFrame) -> bool:
    """Validate required employee columns and structure."""
    if df is None or df.empty:
        logging.error("Data validation failed: DataFrame is empty.")
        return False

    mapped_cols = [COLUMN_MAPPING.get(col, col) for col in df.columns]
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in mapped_cols]

    if missing_columns:
        logging.error(f"Data validation failed. Missing required columns: {missing_columns}")
        return False

    logging.info("All required employee columns are present.")
    return True

def normalize_gdrive_data(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize fields in employee dataframe."""
    df = df.rename(columns=COLUMN_MAPPING)

    if 'Hire Date' in df.columns:
        df['Hire Date'] = pd.to_datetime(df['Hire Date'], errors='coerce').dt.strftime('%Y-%m-%d')

    return df

def main(url: str = DEFAULT_URL, output_csv: str = "gdrive_employees_normalized.csv"):
    try:
        file_path = download_file(url)
        df = read_file(file_path)

        if not validate_data(df):
            logging.error("Data structure validation failed.")
            raise ValueError("Data structure validation failed: missing required columns.")

        normalized_df = normalize_gdrive_data(df)
        normalized_df.to_csv(output_csv, index=False)
        logging.info(f"Scraping and processing completed successfully. Saved to {output_csv}")
        return normalized_df
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    main()
