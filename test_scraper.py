import unittest
from unittest.mock import patch, Mock
import pandas as pd
from scraper import fetch_data, normalize_data, assign_designation, parse_phone
import requests

class TestEmployeeScraper(unittest.TestCase):

    @patch('scraper.requests.get')
    def test_case_1_verify_json_file_download(self, mock_get):
        """Test Case 1: Verify JSON File Download"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [{"id": 1, "first_name": "Test"}]
        mock_get.return_value = mock_response
        
        data = fetch_data("http://dummy_url")
        
        mock_get.assert_called_once_with("http://dummy_url", timeout=10)
        self.assertEqual(data, [{"id": 1, "first_name": "Test"}])

    def test_case_2_verify_json_file_extraction(self):
        """Test Case 2: Verify JSON File Extraction"""
        raw_data = [{"id": 1, "first_name": "John", "last_name": "Doe"}]
        df = normalize_data(raw_data)
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['Full Name'], "John Doe")

    def test_case_3_validate_file_type_and_format(self):
        """Test Case 3: Validate File Type and Format"""
        raw_data = [{"id": 1}, {"id": 2}]
        df = normalize_data(raw_data)
        self.assertEqual(len(df), 2)
        
        df_empty = normalize_data([])
        self.assertTrue(df_empty.empty)

    def test_case_4_validate_data_structure(self):
        """Test Case 4: Validate Data Structure"""
        raw_data = [{
            "id": 1,
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com",
            "phone": "+1-555-1234",
            "gender": "female",
            "age": 30,
            "job_title": "Developer",
            "years_of_experience": 4,
            "salary": 60000,
            "department": "IT"
        }]
        
        df = normalize_data(raw_data)
        
        self.assertIn("Full Name", df.columns)
        self.assertEqual(df.iloc[0]["Full Name"], "Jane Smith")
        self.assertIn("designation", df.columns)
        self.assertEqual(df.iloc[0]["designation"], "data engineer")
        self.assertEqual(df.iloc[0]["phone"], 15551234)
        
    @patch('scraper.requests.get')
    def test_case_5_handle_missing_or_invalid_data(self, mock_get):
        """Test Case 5: Handle Missing or Invalid Data"""
        mock_get.side_effect = requests.exceptions.HTTPError("404 Not Found")
        with self.assertRaises(requests.exceptions.HTTPError):
            fetch_data("http://dummy_url", retries=1)
            
        raw_data = [{
            "first_name": "Bad",
            "last_name": "Phone",
            "phone": "555-1234x99",
            "years_of_experience": "invalid"
        }]
        
        df = normalize_data(raw_data)
        self.assertEqual(df.iloc[0]["phone"], "Invalid Number")
        self.assertTrue(pd.isna(df.iloc[0]["years_of_experience"]))
        self.assertIsNone(df.iloc[0]["designation"])

if __name__ == '__main__':
    unittest.main()
