import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Complete scopes required for Calendar, Drive, and Docs
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/documents'
]

def main():
    credentials_path = "credentials.json"
    token_path = "token.json"

    if not os.path.exists(credentials_path):
        print(f"Error: {credentials_path} not found in the root directory!")
        return

    print("Initializing OAuth 2.0 Flow for Calendar, Drive, and Docs...")
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    creds = flow.run_local_server(port=0)

    # Save the all-in-one token
    with open(token_path, 'w') as token_file:
        token_file.write(creds.to_json())

    print(f"\nSuccess! Full OAuth token saved to '{token_path}'.")

if __name__ == "__main__":
    main()