import os
from typing import Dict, Any, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define required OAuth 2.0 scopes for Drive and Docs access
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/documents'
]


def _has_required_scopes(creds: Optional[Credentials]) -> bool:
    """
    Checks whether the loaded credentials include the scopes needed for Drive and Docs.
    """
    if not creds:
        return False

    granted_scopes = set(getattr(creds, "scopes", []) or [])
    required_scopes = set(SCOPES)
    return required_scopes.issubset(granted_scopes)


def _get_credentials() -> Optional[Credentials]:
    """
    Helper function to load user credentials from local token.json file.
    """
    token_path = "token.json"
    if not os.path.exists(token_path):
        return None
    try:
        return Credentials.from_authorized_user_file(token_path, SCOPES)
    except Exception:
        return None


def create_travel_itinerary_doc(
    folder_name: str,
    doc_title: str,
    content_markdown: str
) -> str:
    """
    Creates a Google Drive folder, generates a Google Doc inside it,
    and populates it with the provided travel itinerary content.

    Parameters:
        folder_name (str): Name of the target folder on Google Drive (e.g., 'Trip_Rome_2026').
        doc_title (str): Title of the Google Document (e.g., 'Rome Trip Itinerary').
        content_markdown (str): The body text / travel summary to write into the document.

    Returns:
        str: Status message containing folder and document links/IDs or error message.
    """
    creds = _get_credentials()
    if not creds or not creds.valid:
        return "Error: OAuth credentials token.json is missing or invalid. Run authentication first."

    if not _has_required_scopes(creds):
        return (
            "Error: token.json is missing the required Google Drive/Docs scopes. "
            "Please re-run setup_oauth.py to authorize Calendar, Drive, and Docs access."
        )

    try:
        # Build Drive and Docs API clients
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)

        # Step 1: Create or locate target folder in Google Drive
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = drive_service.files().create(body=folder_metadata, fields='id, webViewLink').execute()
        folder_id = folder.get('id')
        folder_link = folder.get('webViewLink')

        # Step 2: Create a new blank Google Document inside the created folder
        doc_metadata = {
            'name': doc_title,
            'parents': [folder_id],
            'mimeType': 'application/vnd.google-apps.document'
        }
        doc_file = drive_service.files().create(body=doc_metadata, fields='id').execute()
        doc_id = doc_file.get('id')

        # Step 3: Insert itinerary text into the newly created document
        requests = [
            {
                'insertText': {
                    'location': {
                        'index': 1,
                    },
                    'text': f"{doc_title}\n\n{content_markdown}"
                }
            }
        ]
        
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        doc_link = f"https://docs.google.com/document/d/{doc_id}/edit"

        return (
            f"Successfully created travel document on Google Drive!\n"
            f"- Folder Name: '{folder_name}' (ID: {folder_id})\n"
            f"- Document Title: '{doc_title}'\n"
            f"- Document Link: {doc_link}\n"
            f"- Folder Link: {folder_link}"
        )

    except HttpError as error:
        return f"Google Workspace API HTTP Error: {error}"
    except Exception as e:
        return f"An exception occurred while creating Drive document: {str(e)}"