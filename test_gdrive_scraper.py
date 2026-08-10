import os
import unittest
from unittest.mock import patch, Mock
import pandas as pd
import requests

from gdrive_scraper import (
    download_file,
    identify_file_type,
    read_file,
    validate_data,
    normalize_gdrive_data
)

class TestGDriveEmployeeScraper(unittest.TestCase):

    def setUp(self):
        self.test_csv_path = "test_employees.csv"
        self.test_excel_path = "test_employees.xlsx"
        self.test_invalid_path = "test_invalid.txt"

    def tearDown(self):
        for path in [self.test_csv_path, self.test_excel_path, self.test_invalid_path, "downloaded_employees.csv", "downloaded_employees.xlsx"]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass

    @patch('gdrive_scraper.requests.get')
    def test_case_1_verify_csv_file_download(self, mock_get):
        """Test Case 1: Verify CSV File Download"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {"Content-Type": "text/csv"}
        mock_response.content = b"User Id,First Name,Last Name\n1,Jane,Doe"
        mock_get.return_value = mock_response

        downloaded_path = download_file("http://dummy_url", output_path=self.test_csv_path, retries=1)

        mock_get.assert_called_once_with("http://dummy_url", timeout=10)
        self.assertTrue(os.path.exists(downloaded_path))
        with open(downloaded_path, 'rb') as f:
            content = f.read()
        self.assertIn(b"Jane", content)

    def test_case_2_verify_csv_file_extraction(self):
        """Test Case 2: Verify CSV File Extraction"""
        csv_content = (
            "User Id,First Name,Last Name,Email,Phone,Date of birth,Job Title\n"
            "101,Alice,Smith,alice@example.com,555-0199,2021-05-10,Developer\n"
        )
        with open(self.test_csv_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)

        df = read_file(self.test_csv_path)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['First Name'], "Alice")
        self.assertEqual(df.iloc[0]['Email'], "alice@example.com")

    def test_case_3_validate_file_type_and_format(self):
        """Test Case 3: Validate File Type and Format"""
        # Test CSV detection
        with open(self.test_csv_path, 'w', encoding='utf-8') as f:
            f.write("a,b,c\n1,2,3")
        self.assertEqual(identify_file_type(self.test_csv_path), 'csv')

        # Test Excel detection using magic bytes / extension
        with open(self.test_excel_path, 'wb') as f:
            f.write(b"PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00xl/workbook.xml")
        self.assertEqual(identify_file_type(self.test_excel_path), 'excel')

        # Non-existent file error
        with self.assertRaises(FileNotFoundError):
            identify_file_type("non_existent_file.csv")

    def test_case_4_validate_data_structure(self):
        """Test Case 4: Validate Data Structure"""
        raw_df = pd.DataFrame([{
            "User Id": "1",
            "First Name": "John",
            "Last Name": "Doe",
            "Email": "john@example.com",
            "Phone": "123-456-7890",
            "Date of birth": "1990-01-01",
            "Job Title": "Engineer"
        }])
        self.assertTrue(validate_data(raw_df))

        norm_df = normalize_gdrive_data(raw_df)
        self.assertIn("Employee ID", norm_df.columns)
        self.assertIn("Hire Date", norm_df.columns)
        self.assertIn("Phone Number", norm_df.columns)
        self.assertEqual(norm_df.iloc[0]["Hire Date"], "1990-01-01")

        invalid_df = pd.DataFrame([{
            "User Id": "1",
            "First Name": "John"
        }])
        self.assertFalse(validate_data(invalid_df))

    @patch('gdrive_scraper.requests.get')
    def test_case_5_handle_missing_or_invalid_data(self, mock_get):
        """Test Case 5: Handle Missing or Invalid Data"""
        mock_get.side_effect = requests.exceptions.HTTPError("500 Server Error")
        with self.assertRaises(requests.exceptions.HTTPError):
            download_file("http://dummy_url", retries=2)
        self.assertEqual(mock_get.call_count, 2)

        empty_df = pd.DataFrame()
        self.assertFalse(validate_data(empty_df))

if __name__ == '__main__':
    unittest.main()
