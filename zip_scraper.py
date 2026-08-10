import os
import io
import time
import zipfile
import logging
import requests
import pandas as pd

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

DEFAULT_URL = "https://www.thespreadsheetguru.com/wp-content/uploads/2022/12/EmployeeSampleData.zip"

COLUMN_MAPPING = {
    "EEID": "Employee ID",
    "User Id": "Employee ID",
    "Employee ID": "Employee ID",
    "First Name": "First Name",
    "Last Name": "Last Name",
    "Email": "Email",
    "Job Title": "Job Title",
    "Phone": "Phone Number",
    "Phone Number": "Phone Number",
    "Hire Date": "Hire Date",
    "Date of birth": "Hire Date"
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

def download_and_extract_zip(
    url: str,
    extract_dir: str = "extracted_files",
    zip_path: str = "downloaded_employees.zip",
    retries: int = 3
) -> str:
    """
    Downloads ZIP file from the given URL with retry logic, checks validity,
    and extracts all contents to extract_dir.
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    for attempt in range(retries):
        try:
            logging.info(f"Downloading ZIP file from URL... Attempt {attempt + 1}/{retries}")
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            with open(zip_path, "wb") as f:
                f.write(response.content)

            if not zipfile.is_zipfile(zip_path):
                logging.error("Downloaded file is not a valid ZIP archive.")
                raise ValueError("Downloaded file is not a valid ZIP file.")

            logging.info(f"ZIP file successfully downloaded to {zip_path}. Extracting contents...")
            os.makedirs(extract_dir, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extract_dir)

            logging.info(f"ZIP contents extracted to directory: '{extract_dir}'")
            return extract_dir

        except requests.exceptions.RequestException as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt == retries - 1:
                logging.error("Maximum retry limit reached. ZIP file download failed.")
                raise
            time.sleep(1)
        except Exception as e:
            logging.error(f"Extraction failed: {e}")
            raise

def select_excel_file(extract_dir: str) -> str:
    """
    Scans the extracted directory to find and select the target Excel file (.xlsx or .xls).
    """
    if not os.path.exists(extract_dir) or not os.path.isdir(extract_dir):
        raise FileNotFoundError(f"Extraction directory not found: '{extract_dir}'")

    extracted_files = os.listdir(extract_dir)
    logging.info(f"Extracted files found: {extracted_files}")

    excel_files = [
        f for f in extracted_files
        if f.lower().endswith(('.xlsx', '.xls')) and not f.startswith('~$')
    ]

    if not excel_files:
        logging.error("No valid Excel file (.xlsx / .xls) found inside extracted ZIP contents.")
        raise ValueError("No Excel file found in extracted ZIP archive.")

    # Select the first matching Excel file
    selected_file = os.path.join(extract_dir, excel_files[0])
    logging.info(f"Selected Excel file for processing: '{selected_file}'")
    return selected_file

def read_excel_file(file_path: str) -> pd.DataFrame:
    """
    Reads the Excel file into a pandas DataFrame, validating file format and integrity.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ['.xlsx', '.xls']:
        logging.error(f"Unsupported file format '{ext}' for file: {file_path}")
        raise ValueError(f"Unsupported file format: {ext}")

    try:
        df = pd.read_excel(file_path, engine='openpyxl' if ext == '.xlsx' else None)
        logging.info(f"Excel file read successfully. Shape: {df.shape}. Columns: {list(df.columns)}")
        return df
    except Exception as e:
        logging.error(f"Corrupted or invalid Excel file: {e}")
        raise ValueError(f"Invalid or corrupted Excel file: {e}")

def validate_zip_data(df: pd.DataFrame) -> bool:
    """
    Validates DataFrame structure and presence of required employee fields or mapped equivalents.
    """
    if df is None or df.empty:
        logging.error("Data validation failed: DataFrame is empty.")
        return False

    # Map current columns
    mapped_cols = set()
    for col in df.columns:
        mapped_name = COLUMN_MAPPING.get(col, col)
        mapped_cols.add(mapped_name)

    # If Full Name is present, First Name and Last Name can be derived
    if "Full Name" in df.columns:
        mapped_cols.add("First Name")
        mapped_cols.add("Last Name")

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in mapped_cols]

    # Core required identifiers
    core_required = ["Employee ID", "First Name", "Last Name", "Job Title", "Hire Date"]
    core_missing = [col for col in core_required if col not in mapped_cols]

    if core_missing:
        logging.error(f"Data structure validation failed. Missing core required columns: {core_missing}")
        return False

    if missing_cols:
        logging.warning(f"Some non-core columns missing from source, will be initialized: {missing_cols}")

    logging.info("Data structure validation passed successfully.")
    return True

def normalize_zip_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalizes employee fields: renames mapped columns, splits Full Name if necessary,
    formats dates, and ensures standard output columns exist.
    """
    df = df.copy()

    # Handle Full Name splitting if First Name / Last Name are not present
    if "Full Name" in df.columns and ("First Name" not in df.columns or "Last Name" not in df.columns):
        full_names = df["Full Name"].astype(str).str.strip().str.split(" ", n=1, expand=True)
        if "First Name" not in df.columns:
            df["First Name"] = full_names[0] if full_names.shape[1] > 0 else ""
        if "Last Name" not in df.columns:
            df["Last Name"] = full_names[1] if full_names.shape[1] > 1 else ""

    # Rename mapped columns
    df = df.rename(columns=COLUMN_MAPPING)

    # Format Hire Date to YYYY-MM-DD
    if "Hire Date" in df.columns:
        df["Hire Date"] = pd.to_datetime(df["Hire Date"], errors='coerce').dt.strftime('%Y-%m-%d')

    # Ensure all required output columns exist
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = None

    # Return DataFrame containing at least the standard required columns first
    other_cols = [c for c in df.columns if c not in REQUIRED_COLUMNS]
    ordered_cols = REQUIRED_COLUMNS + other_cols
    return df[ordered_cols]

def main(
    url: str = DEFAULT_URL,
    output_csv: str = "zip_employees_normalized.csv"
) -> pd.DataFrame:
    try:
        extract_dir = download_and_extract_zip(url)
        excel_file = select_excel_file(extract_dir)
        df = read_excel_file(excel_file)

        if not validate_zip_data(df):
            raise ValueError("ZIP employee data structure validation failed.")

        normalized_df = normalize_zip_data(df)
        normalized_df.to_csv(output_csv, index=False)
        logging.info(f"Pipeline completed successfully. Normalized data saved to '{output_csv}'")
        return normalized_df
    except Exception as e:
        logging.error(f"Pipeline execution failed: {e}")
        raise

if __name__ == "__main__":
    main()
