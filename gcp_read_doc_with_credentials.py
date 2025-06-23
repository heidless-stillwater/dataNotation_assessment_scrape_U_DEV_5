import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]


# Specify the document ID
# https://docs.google.com/document/d/e/2PACX-1vTER-wL5E8YC9pxDx43gk8eIds59GtUUk4nJo_ZWagbnrH0NFvMXIw6VWFLpf5tWTZIT9P9oLIoFJ6A/pub
# DOCUMENT_ID = '2PACX-1vQGUck9HIFCyezsrBSnmENk5ieJuYwpt7YHYEzeNJkIb9OSDdx-ov2nRNReKQyey-cwJOoEKUhLmN9z'


# The ID of the Google Doc you want to read.
# Replace with your actual document ID.
DOCUMENT_ID = '1ciO1rXzD5bQIlmEkY0h2OLPwHh25nAsl969rx-XvtP8' # dataNotation assessment data

def read_structural_elements(elements):
    """Recurses through a list of structural elements to read a document's text.
    Args:
        elements: A list of StructuralElement objects.
    Returns:
        The concatenated text from the elements.
    """
    text = ""
    for element in elements:
        if element.get("table"):
            print("table found")
            # Extract text from table cells (tables can be nested)
            table = element.get("table")
            for row in table.get("tableRows"):
                # print(row)
                for cell in row.get("tableCells"):
                    text += read_structural_elements(cell.get("content"))
                    # print(text + "text from table cell")
        # if element.get("paragraph"):
        #     # Extract text from paragraph elements
        #     for run in element.get("paragraph").get("elements"):
        #         if run.get("textRun"):
        #             text += run.get("textRun").get("content")
        # elif element.get("table"):
        #     # Extract text from table cells (tables can be nested)
        #     table = element.get("table")
        #     for row in table.get("tableRows"):
        #         # print(row)
        #         for cell in row.get("tableCells"):
        #             text += read_structural_elements(cell.get("content"))
        #             # print(text + "text from table cell")
        # elif element.get("tableOfContents"):
        #     # Extract text from table of contents (if any)
        #     text += read_structural_elements(
        #         element.get("tableOfContents").get("content")
        #     )
    return text

def data_assemble(document_text):
    """Assembles the data from the document text."""
    # Here you can process the document_text as needed.
    # For example, you might want to split it into lines or paragraphs.
    print("\n--- Document Content ---")
    # print(docusment_text)
    
    num_chars = len(document_text)  
    # for w in range(0, num_chars - 10):
    for w in range(0, 200):
      # print("word", w)
      word = ''
      for r in range(0, 100):
        this_char = document_text[w].strip()
        word += this_char
        w += 1
      print(word)

    print("data_assemble")

def main():
    """Shows how to read the content of a Google Doc."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("docs", "v1", credentials=creds)

        # Retrieve the documents contents from the Docs service.
        document = service.documents().get(documentId=DOCUMENT_ID).execute()

        # Get the title
        title = document.get("title")
        print(f"The title of the document is: {title}")

        # Get the body content
        body_content = document.get("body").get("content")
        document_text = read_structural_elements(body_content)
        
        data_assemble(document_text)      
        
        # print("\n--- Document Content ---")        
        # print(document_text)

    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()