import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define Google Calendar API scopes
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def test_google_calendar_oauth():
    creds = None

    # Check if authorization token already exists
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # Request new credentials if token is missing or expired
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired authorization token...")
            creds.refresh(Request())
        else:
            print("Starting OAuth 2.0 authorization flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save authorization token for future runs
        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())
            print("Authorization token successfully saved to token.json!")

    try:
        # Build the Google Calendar API client
        service = build("calendar", "v3", credentials=creds)

        # Fetch the next 5 upcoming events from the primary calendar
        print("\nFetching upcoming events from Google Calendar...")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                maxResults=5,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])

        print("--- OAUTH 2.0 & CALENDAR API TEST SUCCESSFUL ---")
        if not events:
            print("No upcoming events found, but connection is working!")
        else:
            print("Upcoming Events:")
            for event in events:
                start_time = event["start"].get(
                    "dateTime", event["start"].get("date")
                )
                summary = event.get("summary", "No Title")
                print(f"- {start_time} | {summary}")

    except Exception as error:
        print(f"\nAn error occurred during Calendar API test: {error}")


if __name__ == "__main__":
    test_google_calendar_oauth()