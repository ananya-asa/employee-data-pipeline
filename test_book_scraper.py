import unittest
import os
import csv
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from book_scraper import BookScraper

class TestBookScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = BookScraper()
        self.temp_dir = tempfile.mkdtemp()
        
        self.sample_html = """
        <html><body>
            <article class="product_pod">
                <div class="image_container">
                    <a href="catalogue/a-light-in-the-attic_1000/index.html"><img src="media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg" alt="A Light in the Attic" class="thumbnail"></a>
                </div>
                <p class="star-rating Three">
                    <i class="icon-star"></i>
                    <i class="icon-star"></i>
                    <i class="icon-star"></i>
                    <i class="icon-star"></i>
                    <i class="icon-star"></i>
                </p>
                <h3><a href="catalogue/a-light-in-the-attic_1000/index.html" title="A Light in the Attic">A Light in the ...</a></h3>
                <div class="product_price">
                    <p class="price_color">£51.77</p>
                    <p class="instock availability">
                        <i class="icon-ok"></i>
                        In stock
                    </p>
                </div>
            </article>
        </body></html>
        """
        
        self.sample_missing_html = """
        <html><body>
            <article class="product_pod">
                <!-- Missing rating, availability, url -->
                <h3><a title="Some Title">No Title</a></h3>
                <div class="product_price">
                    <p class="price_color">£10.00</p>
                </div>
            </article>
            <article class="product_pod">
                <!-- Completely invalid, skipped by scraper -->
            </article>
        </body></html>
        """

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_verify_csv_file_download(self):
        """Test Case 1: Verify csv File Download"""
        output_file = os.path.join(self.temp_dir, "test_books.csv")
        data = [{"Title": "Test Book", "Price": "£10.00", "Rating": 5, "Availability": "In stock", "URL": "http://test.com"}]
        self.scraper.save_to_csv(data, filename=output_file)
        
        self.assertTrue(os.path.exists(output_file), "CSV file was not created")
        self.assertTrue(os.path.isfile(output_file), "Created path is not a file")

    def test_verify_csv_file_extraction(self):
        """Test Case 2: Verify csv File Extraction"""
        books, next_url = self.scraper.extract_books_from_page(self.sample_html, "http://books.toscrape.com/")
        
        self.assertEqual(len(books), 1)
        book = books[0]
        
        self.assertEqual(book["Title"], "A Light in the Attic")
        self.assertEqual(book["Price"], "£51.77")
        self.assertEqual(book["Rating"], 3)
        self.assertIn("In stock", book["Availability"])
        self.assertEqual(book["URL"], "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html")
        self.assertIsNone(next_url)

    def test_validate_file_type_and_format(self):
        """Test Case 3: Validate File Type and Format"""
        output_file = os.path.join(self.temp_dir, "test_books.csv")
        data = [{"Title": "T1", "Price": "P1", "Rating": 1, "Availability": "A1", "URL": "U1"}]
        self.scraper.save_to_csv(data, filename=output_file)
        
        self.assertTrue(output_file.endswith(".csv"))
        
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            self.assertEqual(len(header), 5)

    def test_validate_data_structure(self):
        """Test Case 4: Validate Data Structure"""
        output_file = os.path.join(self.temp_dir, "test_books.csv")
        data = [{"Title": "T1", "Price": "P1", "Rating": 1, "Availability": "A1", "URL": "U1"}]
        self.scraper.save_to_csv(data, filename=output_file)
        
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.assertEqual(reader.fieldnames, ["Title", "Price", "Rating", "Availability", "URL"])
            row = next(reader)
            self.assertEqual(row["Title"], "T1")
            self.assertEqual(row["Price"], "P1")
            self.assertEqual(row["Rating"], "1")
            self.assertEqual(row["Availability"], "A1")
            self.assertEqual(row["URL"], "U1")

    def test_handle_missing_or_invalid_data(self):
        """Test Case 5: Handle Missing or Invalid Data"""
        books, _ = self.scraper.extract_books_from_page(self.sample_missing_html, "http://books.toscrape.com/")
        
        self.assertEqual(len(books), 1)
        
        book = books[0]
        self.assertEqual(book["Title"], "Some Title")
        self.assertEqual(book["Price"], "£10.00")
        self.assertEqual(book["Rating"], "Missing Rating")
        self.assertEqual(book["Availability"], "Missing Availability")
        self.assertEqual(book["URL"], "Missing URL")

if __name__ == "__main__":
    unittest.main()
