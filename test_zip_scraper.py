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

    # =============================================================
    # 1. Tests for download_and_extract_zip()
    # =============================================================
    @patch('zip_scraper.requests.get')
    def test_download_and_extract_zip_success(self, mock_get):
        """Verify successful ZIP download and extraction."""
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
        self.assertIn("Employee.xlsx", os.listdir(extracted_dir))

    @patch('zip_scraper.requests.get')
    def test_download_and_extract_zip_http_retry_failure(self, mock_get):
        """Verify HTTP errors trigger max retries and raise exception."""
        mock_get.side_effect = requests.exceptions.HTTPError("500 Server Error")
        with self.assertRaises(requests.exceptions.HTTPError):
            download_and_extract_zip("http://dummy_url/fail.zip", retries=2)
        self.assertEqual(mock_get.call_count, 2)

    @patch('zip_scraper.requests.get')
    def test_download_and_extract_zip_invalid_archive(self, mock_get):
        """Verify downloading non-ZIP bytes raises ValueError."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b"Not a zip content"
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError) as ctx:
            download_and_extract_zip("http://dummy_url/invalid.zip", retries=1)
        self.assertIn("not a valid ZIP", str(ctx.exception))

    # =============================================================
    # 2. Tests for select_excel_file()
    # =============================================================
    def test_select_excel_file_success(self):
        """Verify Excel file selection among multiple non-Excel files."""
        os.makedirs(self.test_extract_dir, exist_ok=True)
        with open(os.path.join(self.test_extract_dir, "notes.txt"), "w") as f:
            f.write("readme")
        with open(os.path.join(self.test_extract_dir, "data.csv"), "w") as f:
            f.write("a,b\n1,2")

        test_df = pd.DataFrame([{"EEID": "E101"}])
        test_df.to_excel(self.test_excel_path, index=False)

        selected = select_excel_file(self.test_extract_dir)
        self.assertTrue(selected.endswith(".xlsx"))

    def test_select_excel_file_no_excel_found(self):
        """Verify raising ValueError when no Excel file exists in directory."""
        os.makedirs(self.test_extract_dir, exist_ok=True)
        with open(self.test_invalid_path, "w") as f:
            f.write("text only")

        with self.assertRaises(ValueError) as ctx:
            select_excel_file(self.test_extract_dir)
        self.assertIn("No Excel file found", str(ctx.exception))

    # =============================================================
    # 3. Tests for read_excel_file()
    # =============================================================
    def test_read_excel_file_success(self):
        """Verify reading a valid Excel file returns a DataFrame."""
        os.makedirs(self.test_extract_dir, exist_ok=True)
        test_df = pd.DataFrame([{"EEID": "E101", "First Name": "Alice"}])
        test_df.to_excel(self.test_excel_path, index=False)

        df = read_excel_file(self.test_excel_path)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["EEID"], "E101")

    def test_read_excel_file_not_found(self):
        """Verify FileNotFoundError for missing file path."""
        with self.assertRaises(FileNotFoundError):
            read_excel_file("non_existent_file.xlsx")

    def test_read_excel_file_unsupported_format(self):
        """Verify ValueError for non-Excel file extension."""
        os.makedirs(self.test_extract_dir, exist_ok=True)
        with open(self.test_invalid_path, "w") as f:
            f.write("random content")

        with self.assertRaises(ValueError) as ctx:
            read_excel_file(self.test_invalid_path)
        self.assertIn("Unsupported file format", str(ctx.exception))

    def test_read_excel_file_corrupted(self):
        """Verify ValueError when reading a corrupted Excel file."""
        os.makedirs(self.test_extract_dir, exist_ok=True)
        corrupted_excel = os.path.join(self.test_extract_dir, "corrupted.xlsx")
        with open(corrupted_excel, "wb") as f:
            f.write(b"NOT_A_VALID_EXCEL_FILE")

        with self.assertRaises(ValueError) as ctx:
            read_excel_file(corrupted_excel)
        self.assertIn("Invalid or corrupted Excel file", str(ctx.exception))

    # =============================================================
    # 4. Tests for validate_zip_data()
    # =============================================================
    def test_validate_zip_data_success(self):
        """Verify validation passes with required columns or mapped aliases."""
        raw_df = pd.DataFrame([{
            "EEID": "E001",
            "Full Name": "John Doe",
            "Job Title": "Software Engineer",
            "Hire Date": "2020/05/10"
        }])
        self.assertTrue(validate_zip_data(raw_df))

    def test_validate_zip_data_empty_df(self):
        """Verify validation fails for empty DataFrame."""
        empty_df = pd.DataFrame()
        self.assertFalse(validate_zip_data(empty_df))

    def test_validate_zip_data_missing_core_columns(self):
        """Verify validation fails when core required columns are missing."""
        invalid_cols_df = pd.DataFrame([{"Other Field": "Value"}])
        self.assertFalse(validate_zip_data(invalid_cols_df))

    # =============================================================
    # 5. Tests for normalize_zip_data()
    # =============================================================
    def test_normalize_zip_data_transformation(self):
        """Verify column mapping, Full Name splitting, date formatting, and column ordering."""
        raw_df = pd.DataFrame([{
            "EEID": "E001",
            "Full Name": "John Doe",
            "Email": "john.doe@example.com",
            "Job Title": "Software Engineer",
            "Phone": "555-1234",
            "Hire Date": "2020/05/10"
        }])

        norm_df = normalize_zip_data(raw_df)

        self.assertIn("Employee ID", norm_df.columns)
        self.assertIn("First Name", norm_df.columns)
        self.assertIn("Last Name", norm_df.columns)
        self.assertIn("Hire Date", norm_df.columns)

        self.assertEqual(norm_df.iloc[0]["Employee ID"], "E001")
        self.assertEqual(norm_df.iloc[0]["First Name"], "John")
        self.assertEqual(norm_df.iloc[0]["Last Name"], "Doe")
        self.assertEqual(norm_df.iloc[0]["Hire Date"], "2020-05-10")

if __name__ == '__main__':
    unittest.main()
