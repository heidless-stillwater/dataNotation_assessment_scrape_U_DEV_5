"""
    Google Docs Table Scraper
    =========================
    This script scrapes tables from a publicly accessible Google Doc and displays them in a mosaic format.
    
    It uses BeautifulSoup for HTML parsing and tabulate for displaying tables.
    
    Usage:
        python gdoc_scrape_0.py <google_doc_url>
        
    The script is designed to handle both published and regular Google Docs URLs.
    
    It extracts the document ID from the provided URL, fetches the document content, and processes the tables using BeautifulSoup.
"""

import requests
from bs4 import BeautifulSoup
import re
from tabulate import tabulate
import sys

def extract_document_id(url):
    """Extract document ID from Google Docs URL - BOILERPLATE"""
    # Pattern for published docs: /d/e/DOCUMENT_ID/pub
    pub_pattern = r'/d/e/([a-zA-Z0-9-_]+)/pub'
    pub_match = re.search(pub_pattern, url)
    if pub_match:
        return pub_match.group(1)
    
    # Pattern for regular docs: /d/DOCUMENT_ID/edit
    edit_pattern = r'/d/([a-zA-Z0-9-_]+)/'
    edit_match = re.search(edit_pattern, url)
    if edit_match:
        return edit_match.group(1)
    
    return None

def convert_to_public_url(url):
    """Convert Google Docs URL to publicly accessible format - BOILERPLATE"""
    doc_id = extract_document_id(url)
    
    if not doc_id:
        return None
    
    # Try the published format first
    if '/pub' in url:
        return f"https://docs.google.com/document/d/e/{doc_id}/pub"
    else:
        # Try to convert edit URL to public format
        return f"https://docs.google.com/document/d/{doc_id}/export?format=html"

def scrape_google_doc_tables(url):
    """
        Scrape tables from a publicly available Google Doc - BOILERPLATE customized re: HTML Parse/BeautifulSoup
        Specifically dealing with tables contained within a Google Doc.
    """
    try:
        # Convert URL to public format if needed
        public_url = convert_to_public_url(url)
        if not public_url:
            print("Error: Could not extract document ID from URL")
            return []
        
        # print(f"Fetching document from: {public_url}")
        
        # Set headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the document
        response = requests.get(public_url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all tables
        tables = soup.find_all('table')
        
        if not tables:
            print("No tables found in the document.")
            return []
        
        extracted_tables = []
        
        for i, table in enumerate(tables):
            
            # Extract table data
            table_data = []
            rows = table.find_all('tr')
            
            for row in rows:
                # Get all cells (td and th)
                cells = row.find_all(['td', 'th'])
                row_data = []
                
                for cell in cells:
                    # Get text content and clean it
                    cell_text = cell.get_text(strip=True)
                    # Handle merged cells (colspan/rowspan)
                    colspan = int(cell.get('colspan', 1))
                    rowspan = int(cell.get('rowspan', 1))
                    
                    # Add the cell content
                    row_data.append(cell_text)
                    
                    # Add empty cells for colspan > 1
                    for _ in range(colspan - 1):
                        row_data.append('')
                
                if row_data:  # Only add non-empty rows
                    table_data.append(row_data)
            
            if table_data:
                extracted_tables.append(table_data)
            
        return extracted_tables
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching document: {e}")
        return []
    except Exception as e:
        print(f"Error processing document: {e}")
        return []

def normalize_table_data(table_data):  
    """    
        Normalize table data to ensure all rows have the same number of columns.
        This is necessary for proper display in a mosaic format. 
        It pads rows with empty strings if they have fewer columns than the maximum.
    """
    # Find the maximum number of columns
    max_cols = max(len(row) for row in table_data) if table_data else 0
    
    # Normalize all rows to have the same number of columns
    normalized_data = []
    for row in table_data:
        # Pad rows with empty strings if they have fewer columns
        padded_row = row + [''] * (max_cols - len(row))
        normalized_data.append(padded_row)
    
    return normalized_data


def display_mosaic(tables):
    """
        Can handle multiple tables from the document.
        Display the scraped tables in a mosaic format.
        Each table is displayed separately, with coordinates and symbols.
    """
    # normalize the data - this is to ensure that all rows in each table have the same number of columns
    for i, table_data in enumerate(tables):
        normalized_data = normalize_table_data(table_data)
        
    # re-format data to enable lookup by coordinates
    # and display in a mosaic format
    for i, table_data in enumerate(tables):
        
        if not table_data:
            print("Empty table")
            continue
        
        # Find the maximum number of columns
        max_cols = max(len(row) for row in table_data) if table_data else 0
        
        # Normalize all rows to have the same number of columns
        normalized_data = []
        for row in table_data:
            # Pad rows with empty strings if they have fewer columns
            padded_row = row + [''] * (max_cols - len(row))
            normalized_data.append(padded_row)
        
        # print(f"Normalized data: {normalized_data}")
        pic_info = {}
        
        # remove first line - Header Info
        normalized_data.pop(0)
        
        # extract & prepare data for display
        num_entries = len(normalized_data)
        max_x = 0
        max_y = 0
        
        for i, row in enumerate(normalized_data):
            # Extract x, y, and symbol from the row
            try:
                x_loc = int(row[0])  # Assuming first column is x coordinate
                y_loc = int(row[2])  # Assuming third column is y coordinate
                symbol = row[1]      # Assuming second column is the symbol
            except ValueError as e:
                print(f"Skipping row {i} due to value error: {e}")
                continue
            
            if x_loc > max_x:
                max_x = x_loc
                
            if y_loc > max_y:
                max_y = y_loc
                
            # print("x_max:", max_x, "y_max:", max_y)
            loc_info = (x_loc, y_loc)
            # print(loc_info)
            pic_info[loc_info] = symbol
             
        ################
        # Display Mosaic
        #
        m_cols = max_x + 1
        m_rows = max_y + 2
        
        # display symbol for each co-ordinate if specified, else display empty space
        print(f"Displaying Mosaic for Table {i + 1} (Size: {m_rows}x{m_cols})")
        print(f"Total Entries: {num_entries}\n")
        
        for y in range(m_rows):
            row_display = []
            # build the row for the current y coordinate
            for x in range(m_cols):
                # Get the symbol for the current location
                symbol = pic_info.get((x, y), ' ')
                row_display.append(symbol)
            # display the row
            print(' '.join(row_display))
            
            
def main():
    
    # Get URL from user
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter the Google Docs URL: ").strip()
    
    if not url:
        print("Error: No URL provided")
        return
    
    # specifically limit to Google Docs URLs
    if 'docs.google.com' not in url:
        print("Error: Please provide a valid Google Docs URL")
        return
    
    print(f"\nProcessing URL: {url}\n")
    
    # Scrape tables
    tables = scrape_google_doc_tables(url)
    
    # Display results
    if tables:
        display_mosaic(tables)
    else:
        print("\nUnable to access document.")

if __name__ == "__main__":
    main()