#
# pip install requests
#
import requests

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# credentials = ... # Load your authenticated credentials

# service = build('docs', 'v1', credentials=credentials)

# document_id = 'YOUR_GOOGLE_DOC_ID_HERE'
# document = service.documents().get(documentId=document_id).execute()

# # The document structure is complex JSON.
# # You would need to iterate through document['body']['content']
# # to find elements of type 'table' and then parse their rows and cells.
# print(document.get('title'))
# # Example of how you might start to look for tables:
# # for element in document.get('body').get('content'):
# #     if 'table' in element:
# #         print("Found a table!")
# #         # Process table rows/cells from element['table']
