import os
import re

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Configuration ---
SCOPES = [
    'https://www.googleapis.com/auth/documents.readonly',
    'https://www.googleapis.com/auth/drive.readonly' # Good to have for broader access, but docs.readonly might suffice
]

SERVICE_ACCOUNT_KEY_FILE = './credentials/service_account_key.json' # Path to your service account JSON key file

# The Google Document ID you want to read
# Using the example from your last valid ID:
DOCUMENT_ID = '1ciO1rXzD5bQIlmEkY0h2OLPwHh25nAsl969rx-XvtP8' # dataNotation assessment data

# --- Authentication Function ---
def get_service_account_creds():
    """Authenticates using a service account."""
    if not os.path.exists(SERVICE_ACCOUNT_KEY_FILE):
        raise FileNotFoundError(
            f"Service account key file not found at: {SERVICE_ACCOUNT_KEY_FILE}\n"
            "Please create a service account and download its JSON key file."
        )
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_KEY_FILE, scopes=SCOPES)
    return creds

# --- Helper Functions to Parse Document Content ---

def read_paragraph_element(element):
    """Returns the text in the given ParagraphElement."""
    text_run = element.get('textRun')
    if text_run is None:
        # This could be due to an inline object (image, drawing, etc.)
        return ""
    return text_run.get('content', '')

def read_structural_elements(elements):
    """
    Recursively reads text from a list of Structural Elements.
    Handles paragraphs, tables, and nested content.
    Returns collected text and extracts table data.
    """
    full_text = []
    tables_data = []

    for element in elements:
        if 'paragraph' in element:
            # It's a paragraph
            paragraph_elements = element.get('paragraph', {}).get('elements', [])
            for p_elem in paragraph_elements:
                full_text.append(read_paragraph_element(p_elem))
        elif 'table' in element:
            # It's a table
            table = element.get('table', {})
            current_table = []
            for row in table.get('tableRows', []):
                current_row = []
                for cell in row.get('tableCells', []):
                    # Table cells can contain nested structural elements
                    cell_content_text, nested_tables = read_structural_elements(cell.get('content', []))
                    current_row.append("".join(cell_content_text))
                    tables_data.extend(nested_tables) # Collect any nested tables

                current_table.append(current_row)
            tables_data.append(current_table) # Add the current table's data
            full_text.append("[TABLE_START]") # Placeholder for table in text flow
            # Optionally, you can insert a formatted representation of the table here if you want it in full_text
            full_text.append("[TABLE_END]")
        elif 'sectionBreak' in element:
            full_text.append("\n--- Section Break ---\n")
        elif 'tableOfContents' in element:
            # TOC also contains structural elements
            toc_content_text, nested_tables = read_structural_elements(element.get('tableOfContents', {}).get('content', []))
            full_text.extend(toc_content_text)
            tables_data.extend(nested_tables)

    return full_text, tables_data

def extract_multi_digit_numbers_as_integers(text):
    # print("Extracting multi-digit integers from text...")
    
    # convert to 'str'
    text = str(text)
    
    # print("\ntext:", text)
    """
    Extracts all multi-digit (or single-digit) integers from a string
    and converts them to integers.
    Returns a list of integers.
    """
    numbers_as_strings = re.findall(r'\d+', text)
    # print("numbers_as_strings:", numbers_as_strings)
    
    numbers_as_integers = [int(num_str) for num_str in numbers_as_strings]
    # print("numbers_as_integers:", numbers_as_integers)
    return numbers_as_integers

# --- Main Function to Get Document and Extract Table Content ---
def get_document_table_contents(document_id):
    creds = get_service_account_creds()

    try:
        service = build('docs', 'v1', credentials=creds)
        
        print(f"Fetching document with ID: {document_id}...")
        # Get the document content
        document = service.documents().get(documentId=document_id).execute()
        
        print(f"Document title: {document.get('title')}")

        body_content = document.get('body', {}).get('content', [])
        
        # Extract all text and tables from the document body
        full_document_text_parts, all_tables_data = read_structural_elements(body_content)

        print("\n--- Extracted Document Text (with table placeholders) ---")
        print("".join(full_document_text_parts))

        print("\n--- Extracted Table Contents ---")
        if not all_tables_data:
            print("No tables found in the document.")
        else:
            for i, table_data in enumerate(all_tables_data):
                print(f"\nTable {i+1}:")
                
                mosaic_data = {
                    "coords": tuple,
                    "shape": str
                }
                
                for row in table_data:
                    xy_coord = extract_multi_digit_numbers_as_integers(row)
                    # print("row:", row)
                    # row_shape = row[1].strip()
                    # print(x_coord, row[0].strip()) 
                    
                    mosaic_data[tuple(xy_coord)] = row[1].strip()
                    
                    # print("row shape:" + row[1])   
                # print(f"mosaic_data: {mosaic_data}")  

        # strip entries where the ley is of type 'str'

        # --- Example 1: Strip entries where the key is an integer (int) ---
        new_dict_no_str_keys = {}
        key_type_to_strip = str

        file_name="./gdoc_log.txt"

        for key, value in mosaic_data.items():
            if not isinstance(key, key_type_to_strip):
                if len(key) > 0:
                  new_dict_no_str_keys[key] = value          
                with open(file_name, 'a') as f:
                    f.write(str(key))
                    # f.write(str(type(key)))
        
        # file_name="./gdoc_log.txt"
        # for key in new_dict_no_str_keys:
          # print("type(key):", type(key))
          # print(f"Key: {key} :: shape: {clean_data[key]}")
          # x_coord, y_coord = key


        # return all_tables_data
        
        # print("new_dict_no_str_keys:", new_dict_no_str_keys)
        
            
        # print(f"Key: {key} :: {type(key)} :: shape: {clean_data[key]}")
        # if len(key) == 0:
        #  print("Key is nil, skipping...")  
        
        
        return new_dict_no_str_keys


    except HttpError as error:
        print(f"An HTTP error occurred: {error}")
        if error.resp.status == 403:
            print("Permission denied. Ensure the service account has 'Viewer' access to the Google Doc.")
            print(f"Service account email: {creds.service_account_email}")
            print("You might need to share the Google Doc explicitly with this email address.")
        elif error.resp.status == 404:
            print("Document not found. Please double-check the Document ID and its accessibility.")
    except FileNotFoundError as fnfe:
        print(f"Error: {fnfe}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return None

def draw_matrix(clean_data):
  status = "success"
  print("drawing matrix\n")
  

  # print("--- Iterating through keys ---")
  
  # file_name="./gdoc_log.txt"
  # open(file_name, mode='a', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None)

  for key in clean_data:
    x = 1
    # print("type(key):", type(key))
    
    # print(f"Key: {key} :: {type(key)} :: shape: {clean_data[key]}")
    # print(f"Key: {key} :: shape: {clean_data[key]}")
    
    # if len(key) == 0:
    #  print("Key is nil, skipping...")  
 
    # x_coord, y_coord = key
    # #   print(f"Coordinates: {x_coord}, {y_coord} - Shape: {shape}")
    # print(f"Coordinates: {x_coord}, {y_coord}")


    # with open(file_name, 'a') as f:
    #     # f.write(str(key))
    #     if type(key) == tuple:
    #       f.write(str(type(key)))

    # print(f"Content appended to '{file_name}'.")

    # # Append another line
    # another_entry = "Another log entry: Data updated at 2025-06-21 14:05:30\n"
    # with open(file_name, 'a') as f:
    #     f.write(another_entry)
    # print(f"Another line appended to '{file_name}'.")

    # # Verify content (optional)
    # with open(file_name, 'r') as f:
    #     print("\nContent of the file:")
    #     print(f.read())

    # x_coord = key[0]
    # y_coord = key[1]
    # shape = clean_data[key]
    # print(f"Coordinates: {x_coord}")
    # print(f"Coordinates: {x_coord}, {y_coord} - Shape: {shape}")

  # data meta
  max_x_tup = max(clean_data.items(), key=lambda item: item[0][0])
  max_x = max_x_tup[0][0]
  print("max_x:", max_x)
  
  max_y_tup = max(clean_data.items(), key=lambda item: item[0][1])
  max_y = max_y_tup[0][1]
  print("max_y:", max_y)

  for y in range(max_y + 1):
    # print("y:", y)
    for x in range(max_x):
      # print(f"Coordinates: {x}, {y}")
      if (x, y) in clean_data:
        shape = clean_data[(x, y)]
        # print(f"Coordinates: {x}, {y} - Shape: {shape}")
        print(shape, end='')
      else:
        print(' ', end='')
        
    print("\n")

  # matrix meta
  # for key in clean_data:
  #   x_coord, y_coord = key
  #   shape = clean_data[key]
  #   print(f"Coordinates: {x_coord}, {y_coord} - Shape: {shape}")
  # print("clean_data:", clean_data)

    # with open(file_name, 'a') as f:
    #     f.write(new_entry)

    # print(f"Content appended to '{file_name}'.")

    # # Append another line
    # another_entry = "Another log entry: Data updated at 2025-06-21 14:05:30\n"
    # with open(file_name, 'a') as f:
    #     f.write(another_entry)
    # print(f"Another line appended to '{file_name}'.")

    # # Verify content (optional)
    # with open(file_name, 'r') as f:
    #     print("\nContent of the file:")
    #     print(f.read())

  
  return status

# --- Run the script ---
if __name__ == '__main__':
    clean_data = get_document_table_contents(DOCUMENT_ID)
    
    # print(clean_data)
    
    draw_matrix(clean_data)