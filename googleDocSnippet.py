import random
from myid import GoogleDocKeys
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

my = GoogleDocKeys()

# Initialize the API client
scopes = ['https://www.googleapis.com/auth/documents.readonly']
credentials = Credentials.from_service_account_file(my.CREDENTIAL_FILE, scopes=scopes)
service = build('docs', 'v1', credentials=credentials)

# The ID of the Google Doc
document_id = my.DOCUMENT_ID

# Fetch the document
document = service.documents().get(documentId=document_id).execute()

# SKIP when HEADING_3 and "参考文献"
# skip the segment if HEADING_3 and heading_text is "参考文献"

# Parse the document content
headings = []
segment_content = []
current_segment = []
pending_heading = None  # Store the current heading and append it to the list only if the segment has content
start_storing = False  # Flag to start storing segment content only after encountering the first heading
current_level = 0  # 0 means we are not inside any heading level

for element in document['body']['content']:
    if 'paragraph' in element:
        # Check for new segment heading
        if 'namedStyleType' in element['paragraph']['paragraphStyle']:
            if element['paragraph']['paragraphStyle']['namedStyleType'] == 'HEADING_2':
                # Start storing text content once we encounter the first heading
                start_storing = True
                
                # Save previous segment content if it's not just whitespace
                if current_segment:
                    joined_segment = '. '.join(current_segment).strip()
                    if joined_segment:  # Check if the joined text is not just whitespace
                        segment_content.append(joined_segment)
                        if pending_heading:  # Only append the heading if the segment has content
                            headings.append(pending_heading)
                        current_segment = []

                # Store the new heading temporarily; don't add it to the list yet
                heading_text = ""
                for part in element['paragraph']['elements']:
                    if 'textRun' in part:
                        heading_text += part['textRun']['content']
                pending_heading = heading_text.strip()
                continue

        # Collect text content for the current segment only if start_storing is True
        if start_storing:
            paragraph_text = ""
            for part in element['paragraph']['elements']:
                if 'textRun' in part:
                    paragraph_text += part['textRun']['content']

            sentences = paragraph_text.split('. ')
            current_segment.extend(sentences)

# Save the last segment's content if it's not just whitespace
if current_segment:
    joined_segment = '. '.join(current_segment).strip()
    if joined_segment:
        segment_content.append(joined_segment)
        if pending_heading:
            headings.append(pending_heading)

num_sentences = 3  # Number of continuous sentences to extract

for i, content in enumerate(segment_content):
    if i not in [0, 6, 8, 26, 28]:
        sentences = segment_content[i].split('. ')
        sentences = [s for s in sentences if s.strip()]

        if len(sentences) > num_sentences:  # Only proceed if the segment has enough sentences
            start_index = random.randint(0, len(sentences) - num_sentences)
            end_index = start_index + num_sentences
            extracted_sentences = sentences[start_index:end_index]
            print(f"{i}:「{headings[i]}」")
            print(''.join(extracted_sentences),"\n")
