import os
import io
import shutil
import zipfile
import unittest
from unittest.mock import patch, Mock
import pandas as pd
import requests

from zip_scraper import (
    download_and_extract_zip,
    select_excel_file,
    read_excel_file,
    validate_zip_data,
    normalize_zip_data
)

class TestZipEmployeeScraper(unittest.TestCase):

    def setUp(self):
        self.test_extract_dir = "test_extracted_files"
        self.test_zip_path = "test_employees.zip"
        self.test_excel_path = os.path.join(self.test_extract_dir, "test_employees.xlsx")
        self.test_invalid_path = os.path.join(self.test_extract_dir, "test_invalid.txt")

    def tearDown(self):
        if os.path.exists(self.test_extract_dir):
            shutil.rmtree(self.test_extract_dir, ignore_errors=True)
        for path in [self.test_zip_path, "downloaded_employees.zip", "zip_employees_normalized.csv"]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass

    def _create_mock_zip(self, files_dict, zip_filename=None):
        """Helper to create a zip file with string/bytes content."""
        target_zip = zip_filename or self.test_zip_path
        with zipfile.ZipFile(target_zip, 'w') as zf:
            for fname, content in files_dict.items():
                if isinstance(content, str):
                    content = content.encode('utf-8')
                zf.writestr(fname, content)
        with open(target_zip, 'rb') as f:
            return f.read()

    # -------------------------------------------------------------
    # Test Case 1: Verify EXCEL File Download (ZIP Download)
    # -------------------------------------------------------------
    @patch('zip_scraper.requests.get')
    def test_case_1_verify_excel_file_download(self, mock_get):
        """Test Case 1: Verify EXCEL / ZIP File Download with retries and valid ZIP check."""
        # Create valid zip bytes
        zip_bytes = self._create_mock_zip({"Employee.xlsx": b"mock_content"})

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = zip_bytes
        mock_get.return_value = mock_response

        extracted_dir = download_and_extract_zip(
            "http://dummy_url/data.zip",
            extract_dir=self.test_extract_dir,
            zip_path=self.test_zip_path,
            retries=1
        )

        mock_get.assert_called_once_with(
            "http://dummy_url/data.zip",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            timeout=15
        )
        self.assertTrue(os.path.exists(extracted_dir))
        extracted_files = os.listdir(extracted_dir)
        self.assertIn("Employee.xlsx", extracted_files)

    # -------------------------------------------------------------
    # Test Case 2: Verify EXCEL File Extraction
    # -------------------------------------------------------------
    def test_case_2_verify_excel_file_extraction(self):
        """Test Case 2: Verify ZIP Extraction and correct Excel file selection among multiple files."""
        os.makedirs(self.test_extract_dir, exist_ok=True)

        # Create multiple files in extract directory (txt, csv, and target xlsx)
        with open(os.path.join(self.test_extract_dir, "notes.txt"), "w") as f:
            f.write("readme file")
        with open(os.path.join(self.test_extract_dir, "data.csv"), "w") as f:
            f.write("a,b,c\n1,2,3")

        test_df = pd.DataFrame([{
            "EEID": "E101",
            "First Name": "Alice",
            "Last Name": "Smith",
            "Job Title": "Data Analyst",
            "Hire Date": "2022-01-15"
        }])
        test_df.to_excel(self.test_excel_path, index=False)

        selected_file = select_excel_file(self.test_extract_dir)
        self.assertTrue(selected_file.endswith(".xlsx"))

        df = read_excel_file(selected_file)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["EEID"], "E101")
        self.assertEqual(df.iloc[0]["First Name"], "Alice")

    # -------------------------------------------------------------
    # Test Case 3: Validate File Type and Format
    # -------------------------------------------------------------
    def test_case_3_validate_file_type_and_format(self):
        """Test Case 3: Validate File Type and Format (detecting invalid formats & corrupted Excel files)."""
        os.makedirs(self.test_extract_dir, exist_ok=True)

        # Non-existent file error
        with self.assertRaises(FileNotFoundError):
            read_excel_file("non_existent_file.xlsx")

        # Unsupported file extension error
        with open(self.test_invalid_path, "w") as f:
            f.write("random content")

        with self.assertRaises(ValueError) as ctx:
            read_excel_file(self.test_invalid_path)
        self.assertIn("Unsupported file format", str(ctx.exception))

        # Corrupted Excel file error (.xlsx with invalid binary content)
        corrupted_excel = os.path.join(self.test_extract_dir, "corrupted.xlsx")
        with open(corrupted_excel, "wb") as f:
            f.write(b"NOT_A_ZIP_OR_EXCEL_FILE")

        with self.assertRaises(ValueError) as ctx:
            read_excel_file(corrupted_excel)
        self.assertIn("Invalid or corrupted Excel file", str(ctx.exception))

    # -------------------------------------------------------------
    # Test Case 4: Validate Data Structure
    # -------------------------------------------------------------
    def test_case_4_validate_data_structure(self):
        """Test Case 4: Validate Data Structure, column mapping, name splitting, and date normalization."""
        raw_df = pd.DataFrame([{
            "EEID": "E001",
            "Full Name": "John Doe",
            "Email": "john.doe@example.com",
            "Job Title": "Software Engineer",
            "Phone": "555-1234",
            "Hire Date": "2020/05/10"
        }])

        self.assertTrue(validate_zip_data(raw_df))

        norm_df = normalize_zip_data(raw_df)

        self.assertIn("Employee ID", norm_df.columns)
        self.assertIn("First Name", norm_df.columns)
        self.assertIn("Last Name", norm_df.columns)
        self.assertIn("Hire Date", norm_df.columns)

        self.assertEqual(norm_df.iloc[0]["Employee ID"], "E001")
        self.assertEqual(norm_df.iloc[0]["First Name"], "John")
        self.assertEqual(norm_df.iloc[0]["Last Name"], "Doe")
        self.assertEqual(norm_df.iloc[0]["Hire Date"], "2020-05-10")

    # -------------------------------------------------------------
    # Test Case 5: Handle Missing or Invalid Data
    # -------------------------------------------------------------
    @patch('zip_scraper.requests.get')
    def test_case_5_handle_missing_or_invalid_data(self, mock_get):
        """Test Case 5: Handle Missing or Invalid Data (retry failures, invalid ZIPs, missing required columns)."""
        # Download failure after max retries
        mock_get.side_effect = requests.exceptions.HTTPError("500 Server Error")
        with self.assertRaises(requests.exceptions.HTTPError):
            download_and_extract_zip("http://dummy_url/fail.zip", retries=2)
        self.assertEqual(mock_get.call_count, 2)

        # Invalid ZIP file download (not a ZIP archive)
        mock_get.reset_mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b"Not a zip content"
        mock_get.side_effect = None
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError) as ctx:
            download_and_extract_zip("http://dummy_url/invalid.zip", retries=1)
        self.assertIn("not a valid ZIP", str(ctx.exception))

        # ZIP containing no Excel file
        os.makedirs(self.test_extract_dir, exist_ok=True)
        with open(self.test_invalid_path, "w") as f:
            f.write("only text file here")

        with self.assertRaises(ValueError) as ctx:
            select_excel_file(self.test_extract_dir)
        self.assertIn("No Excel file found", str(ctx.exception))

        # Empty DataFrame validation failure
        empty_df = pd.DataFrame()
        self.assertFalse(validate_zip_data(empty_df))

        # Missing core columns validation failure
        invalid_cols_df = pd.DataFrame([{"Other Field": "Value"}])
        self.assertFalse(validate_zip_data(invalid_cols_df))

if __name__ == '__main__':
    unittest.main()
