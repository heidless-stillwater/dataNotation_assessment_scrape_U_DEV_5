#!/usr/bin/env python3
"""
Google Docs Table Scraper
Scrapes tabular data from publicly available Google Docs and displays it in tabular format.
"""

import requests
from bs4 import BeautifulSoup
import re
from tabulate import tabulate
import sys

def extract_document_id(url):
    """Extract document ID from Google Docs URL"""
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
    """Convert Google Docs URL to publicly accessible format"""
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
    """Scrape tables from a publicly available Google Doc"""
    try:
        # Convert URL to public format if needed
        public_url = convert_to_public_url(url)
        if not public_url:
            print("Error: Could not extract document ID from URL")
            return []
        
        print(f"Fetching document from: {public_url}")
        
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
            print(f"\n--- Processing Table {i + 1} ---")
            
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

def display_tables(tables):
    """Display tables in formatted output"""
    if not tables:
        print("No tables to display.")
        return
    
    for i, table_data in enumerate(tables):
        print(f"\n{'='*60}")
        print(f"TABLE {i + 1}")
        print(f"{'='*60}")
        
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
        
        # Display using tabulate for better formatting
        try:
            # Try to use first row as headers if it looks like headers
            if len(normalized_data) > 1:
                headers = normalized_data[0]
                data = normalized_data[1:]
                print(tabulate(data, headers=headers, tablefmt='grid'))
            else:
                print(tabulate(normalized_data, tablefmt='grid'))
        except:
            # Fallback to simple display
            for j, row in enumerate(normalized_data):
                print(f"Row {j + 1}: {' | '.join(str(cell) for cell in row)}")
        
        print(f"\nTable dimensions: {len(normalized_data)} rows × {max_cols} columns")

def main():
    """Main function"""
    print("Google Docs Table Scraper")
    print("=" * 40)
    
    # Get URL from user
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter the Google Docs URL: ").strip()
    
    if not url:
        print("Error: No URL provided")
        return
    
    if 'docs.google.com' not in url:
        print("Error: Please provide a valid Google Docs URL")
        return
    
    print(f"\nProcessing URL: {url}")
    
    # Scrape tables
    tables = scrape_google_doc_tables(url)
    
    # Display results
    if tables:
        print(f"\nFound {len(tables)} table(s) in the document:")
        display_tables(tables)
    else:
        print("\nNo tables found or unable to access the document.")
        print("\nTroubleshooting tips:")
        print("1. Make sure the document is publicly accessible")
        print("2. Try using the 'Published to web' URL format")
        print("3. Check if the document contains actual HTML tables")

if __name__ == "__main__":
    main()