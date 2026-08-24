import requests

from bs4 import BeautifulSoup # type: ignore
import csv
import logging
from urllib.parse import urljoin

# Setup basic logging to output information and errors
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class BookScraper:
    def __init__(self, base_url="http://books.toscrape.com/"):
        self.base_url = base_url
        # Mapping string class names for ratings to numeric values
        self.rating_mapping = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }

    def fetch_page(self, url):
        """Fetches the HTML content of the page."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Check for HTTP errors
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching URL {url}: {e}")
            return None

    def extract_books_from_page(self, html_content, current_url):
        """Extracts book details from the provided HTML content."""
        books = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # All books are within 'article' tags with class 'product_pod'
        book_articles = soup.find_all('article', class_='product_pod')
        
        for article in book_articles:
            try:
                # Extract Title
                h3 = article.find('h3')
                a_tag = h3.find('a') if h3 else None
                title = a_tag['title'] if a_tag and a_tag.has_attr('title') else "Missing Title"

                # Extract Price
                price_p = article.find('p', class_='price_color')
                price = price_p.text.strip() if price_p else "Missing Price"

                # Extract Rating
                rating_p = article.find('p', class_='star-rating')
                rating = "Missing Rating"
                if rating_p:
                    # The class list contains 'star-rating' and the actual rating (e.g., 'Three')
                    classes = rating_p.get('class', [])
                    for cls in classes:
                        if cls in self.rating_mapping:
                            rating = self.rating_mapping[cls]
                            break

                # Extract Availability
                availability_p = article.find('p', class_='instock availability')
                availability = availability_p.text.strip() if availability_p else "Missing Availability"

                # Extract Product URL
                if a_tag and a_tag.has_attr('href'):
                    relative_url = a_tag['href']
                    # Handle relative URLs correctly depending on whether we are on the catalogue pages or homepage
                    product_url = urljoin(current_url, relative_url)
                else:
                    product_url = "Missing URL"

                book_data = {
                    "Title": title,
                    "Price": price,
                    "Rating": rating,
                    "Availability": availability,
                    "URL": product_url
                }
                
                # Basic check to skip completely invalid entries
                if title != "Missing Title" and price != "Missing Price":
                    books.append(book_data)
                else:
                    logging.warning(f"Skipping a book due to missing core fields. Extracted data: {book_data}")

            except Exception as e:
                logging.error(f"Error extracting book data: {e}")
                continue # Skip this book if a critical error occurs
                
        # Find next page link
        next_page = soup.find('li', class_='next')
        next_url = None
        if next_page:
            next_a = next_page.find('a')
            if next_a and next_a.has_attr('href'):
                next_url = urljoin(current_url, next_a['href'])
                
        return books, next_url

    def scrape(self, start_url=None, max_pages=None):
        """Main scraping loop that handles pagination."""
        url = start_url or self.base_url
        all_books = []
        pages_scraped = 0
        
        logging.info("Starting scraping process...")
        while url:
            if max_pages and pages_scraped >= max_pages:
                break
                
            logging.info(f"Scraping page: {url}")
            html = self.fetch_page(url)
            if not html:
                logging.error(f"Failed to fetch {url}. Stopping pagination.")
                break
                
            books, next_url = self.extract_books_from_page(html, url)
            all_books.extend(books)
            logging.info(f"Extracted {len(books)} books from this page.")
            
            url = next_url
            pages_scraped += 1
            
        logging.info(f"Scraping completed. Total books extracted: {len(all_books)}")
        return all_books

    def save_to_csv(self, books, filename="books_data.csv"):
        """Saves a list of dictionary book data to a CSV file."""
        if not books:
            logging.warning("No books to save.")
            return

        keys = ["Title", "Price", "Rating", "Availability", "URL"]
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                dict_writer = csv.DictWriter(f, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(books)
            logging.info(f"Data successfully saved to {filename}")
        except IOError as e:
            logging.error(f"Failed to save data to {filename}: {e}")

if __name__ == "__main__":
    # If run directly, scrape everything and save
    scraper = BookScraper()
    # By default, scrapes all pages. For testing a small set, pass max_pages=1
    data = scraper.scrape()
    scraper.save_to_csv(data)
