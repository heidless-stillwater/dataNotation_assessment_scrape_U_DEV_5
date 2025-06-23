from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def read_tables_from_google_doc(document_id, creds):
    service = build('docs', 'v1', credentials=creds)
    doc = service.documents().get(documentId=document_id).execute()
    
    content = doc.get('body').get('content')
    tables = []
    
    for element in content:
        if 'table' in element:
            table = element.get('table')
            table_data = []
            
            for row in table.get('tableRows', []):
                row_data = []
                for cell in row.get('tableCells', []):
                    cell_text = ''
                    for content_element in cell.get('content', []):
                        if 'paragraph' in content_element:
                            paragraph = content_element.get('paragraph')
                            for element in paragraph.get('elements', []):
                                if 'textRun' in element:
                                    cell_text += element.get('textRun').get('content', '')
                    row_data.append(cell_text.strip())
                table_data.append(row_data)
            tables.append(table_data)
    
    return tables