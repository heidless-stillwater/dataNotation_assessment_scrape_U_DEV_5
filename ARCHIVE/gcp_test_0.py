#
# pip install requests
#
import requests

#########################################
# assuming credentials required - FOR NOW
# created SERVICE_ACCOv# project:
# project: python-scratch-2
# svc account:my-docs-sa@python-scratch-2.iam.gserviceaccount.comUNT 
#SERVICE_ACCOUNT_KEY_FILE = './credentials/service_account_key.json'

# Google Document ID
# assessment provided proving problematic.
# https://docs.google.com/document/d/e/2PACX-1vTER-wL5E8YC9pxDx43gk8eIds59GtUUk4nJo_ZWagbnrH0NFvMXIw6VWFLpf5tWTZIT9P9oLIoFJ6A/pub
# document_id = '2PACX-1vTER-wL5E8YC9pxDx43gk8eIds59GtUUk4nJo_ZWagbnrH0NFvMXIw6VWFLpf5tWTZIT9P9oLIoFJ6A'
#
# For now, using a different document ID. public URL linking to a copy of the assessment link
# dataNotation-assessment-data : https://docs.google.com/document/d/1ciO1rXzD5bQIlmEkY0h2OLPwHh25nAsl969rx-XvtP8/edit?tab=t.0
# DOCUMENT_ID = '1ciO1rXzD5bQIlmEkY0h2OLPwHh25nAsl969rx-XvtP8' # dataNotation assessment data


# Example: A public CSV file hosted on GitHub (often found via Google search)
# Replace this with your actual Google Public URL
public_url_text = "https://raw.githubusercontent.com/datasets/gdp/main/data/gdp_md.csv"

# Example: A public JSON file
public_url_json = "https://jsonplaceholder.typicode.com/todos/1" # Public API endpoint, but serves JSON

public_url_doc = "https://docs.google.com/document/d/e/2PACX-1vTER-wL5E8YC9pxDx43gk8eIds59GtUUk4nJo_ZWagbnrH0NFvMXIw6VWFLpf5tWTZIT9P9oLIoFJ6A/pub"

def read_public_document_doc(url):
    print(f"Reading document from {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        # For text-based files (like .txt, .csv, .json)
        document_content = response.text
        print(f"--- Content from {url} ---")
        print(document_content[:500]) # Print first 500 characters
        print("...")
        return document_content

    except requests.exceptions.RequestException as e:
        print(f"Error reading document from {url}: {e}")
        return None

# Read a DOC file
doc_content = read_public_document_doc(public_url_doc)
if doc_content:
    print("\nDoc content successfully retrieved.")
    # You can then parse the CSV content, e.g., using io.StringIO and csv module
    # import csv
    # import io
    # csv_file = io.StringIO(csv_content)
    # reader = csv.reader(csv_file)
    # for row in reader:
    #     print(row)
    
#######################################
# def read_public_document_text(url):
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

#         # For text-based files (like .txt, .csv, .json)
#         document_content = response.text
#         print(f"--- Content from {url} ---")
#         print(document_content[:500]) # Print first 500 characters
#         print("...")
#         return document_content

#     except requests.exceptions.RequestException as e:
#         print(f"Error reading document from {url}: {e}")
#         return None

# # Read a text/CSV file
# csv_content = read_public_document_text(public_url_text)
# if csv_content:
#     print("\nCSV content successfully retrieved.")
#     # You can then parse the CSV content, e.g., using io.StringIO and csv module
#     # import csv
#     # import io
#     # csv_file = io.StringIO(csv_content)
#     # reader = csv.reader(csv_file)
#     # for row in reader:
#     #     print(row)

# # Read a JSON file
# json_content_str = read_public_document_text(public_url_json)
# if json_content_str:
#     print("\nJSON content successfully retrieved.")
#     # You can parse the JSON string into a Python dictionary/list
#     import json
#     json_data = json.loads(json_content_str)
#     print(f"Parsed JSON data: {json_data}")
    
