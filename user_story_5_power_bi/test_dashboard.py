import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import unittest
import pandas as pd

class TestPowerBIDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.csv_path = "books_data.csv"
        # If running from within subfolder or root, locate the CSV dynamically
        if not os.path.exists(cls.csv_path):
            cls.csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "user_story_4_book_scraper", "books_data.csv")
            
        # Load and clean data mimicking Power Query M transformations
        cls.df = pd.read_csv(cls.csv_path, encoding='utf-8')
        cls.df['Title'] = cls.df['Title'].astype(str).str.strip()
        
        # Clean price (remove Â, £, and spaces)
        cls.df['Price_GBP'] = cls.df['Price'].astype(str).str.replace('Â', '', regex=False)
        cls.df['Price_GBP'] = cls.df['Price_GBP'].str.replace('£', '', regex=False)
        cls.df['Price_GBP'] = cls.df['Price_GBP'].str.replace(' ', '', regex=False)
        cls.df['Price_GBP'] = pd.to_numeric(cls.df['Price_GBP'], errors='coerce')
        
        cls.df['Rating'] = pd.to_numeric(cls.df['Rating'], errors='coerce').fillna(0).astype(int)
        cls.df['Availability'] = cls.df['Availability'].astype(str).str.strip()
        cls.df['URL'] = cls.df['URL'].astype(str).str.strip()
        
        # Remove duplicates like Power Query
        cls.df = cls.df.drop_duplicates(subset=['Title', 'URL'])
        
        # Convert Price to USD (using 1.32 conversion rate)
        cls.df['Price_USD'] = cls.df['Price_GBP'] * 1.32
        
        # Categorize into Budget, Standard, Premium
        def categorize(price):
            if price < 26.40:
                return "Budget"
            elif price <= 66.00:
                return "Standard"
            else:
                return "Premium"
        cls.df['Price Category'] = cls.df['Price_USD'].apply(categorize)

    def test_tc1_csv_import(self):
        """Test Case 1: Validate successful import of CSV data"""
        self.assertTrue(os.path.exists(self.csv_path), "CSV file does not exist")
        self.assertGreater(len(self.df), 0, "No records found in CSV")
        self.assertEqual(len(self.df), 1000, "Expected 1000 unique records after deduplication")

    def test_tc2_data_types(self):
        """Test Case 2: Validate correct data type assignments"""
        self.assertTrue(pd.api.types.is_numeric_dtype(self.df['Price_GBP']), "Price_GBP must be numeric")
        self.assertTrue(pd.api.types.is_numeric_dtype(self.df['Price_USD']), "Price_USD must be numeric")
        self.assertTrue(pd.api.types.is_integer_dtype(self.df['Rating']), "Rating must be integer")
        self.assertTrue(pd.api.types.is_string_dtype(self.df['Availability']), "Availability must be string/text")
        self.assertTrue(pd.api.types.is_string_dtype(self.df['Title']), "Title must be string/text")

    def test_tc3_filtering(self):
        """Test Case 3: Validate filtering by rating and availability"""
        # Filter by 5-star Rating and In stock availability
        filtered_5_star = self.df[(self.df['Rating'] == 5) & (self.df['Availability'].str.lower() == 'in stock')]
        self.assertEqual(len(filtered_5_star), 196, "Expected 196 books with 5-star rating and In stock availability")
        
        # Filter by 1-star Rating and In stock availability
        filtered_1_star = self.df[(self.df['Rating'] == 1) & (self.df['Availability'].str.lower() == 'in stock')]
        self.assertEqual(len(filtered_1_star), 226, "Expected 226 books with 1-star rating and In stock availability")

    def test_tc4_calculations_and_grouping(self):
        """Test Case 4: Verify calculation accuracy for average price and category grouping"""
        # Overall average price check
        overall_avg = self.df['Price_USD'].mean()
        self.assertAlmostEqual(overall_avg, 46.2937, places=2, msg="Overall average price USD is incorrect")
        
        # Category grouping count validation
        counts = self.df['Price Category'].value_counts()
        self.assertEqual(counts.get("Budget", 0), 196, "Expected 196 Budget books (< $26.40)")
        self.assertEqual(counts.get("Standard", 0), 606, "Expected 606 Standard books ($26.40 - $66.00)")
        self.assertEqual(counts.get("Premium", 0), 198, "Expected 198 Premium books (> $66.00)")

    def test_tc5_slicer_dynamic_updates(self):
        """Test Case 5: Confirm that metrics update dynamically when sliced by Rating"""
        # When sliced to rating 3
        sliced_df = self.df[self.df['Rating'] == 3]
        self.assertEqual(len(sliced_df), 203, "Expected 203 books for rating 3")
        self.assertAlmostEqual(sliced_df['Price_USD'].mean(), 45.7924, places=2, msg="Average price for rating 3 is incorrect")

    def test_tc6_consistent_format(self):
        """Test Case 6: Check for consistent data format and no visual errors (no null values or invalid ranges)"""
        self.assertFalse(self.df['Price_USD'].isnull().any(), "Price_USD column contains nulls")
        self.assertFalse(self.df['Rating'].isnull().any(), "Rating column contains nulls")
        self.assertFalse(self.df['Price Category'].isnull().any(), "Price Category contains nulls")
        self.assertTrue((self.df['Rating'] >= 1).all() and (self.df['Rating'] <= 5).all(), "Ratings must be between 1 and 5")

if __name__ == '__main__':
    unittest.main()
