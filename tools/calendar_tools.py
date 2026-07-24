import os.path
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    """Authenticates and returns the Google Calendar API service instance."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise PermissionError(
                "Valid token.json not found. Please run test_oauth.py first."
            )

    return build("calendar", "v3", credentials=creds)


def add_calendar_event(
    summary: str,
    location: str,
    description: str,
    start_time_iso: str,
    end_time_iso: str,
    timezone: str = "Europe/Warsaw",
) -> str:
    """Creates a new event in the user's primary Google Calendar.

    Args:
        summary: Title of the event (e.g., 'Flight to Rome', 'Hotel Booking').
        location: Location or address of the event.
        description: Detailed summary or reservation information.
        start_time_iso: Start date and time in ISO format (YYYY-MM-DDTHH:MM:SS).
        end_time_iso: End date and time in ISO format (YYYY-MM-DDTHH:MM:SS).
        timezone: Timezone string (default: 'Europe/Warsaw').

    Returns:
        Confirmation message with event ID and link.
    """
    try:
        service = get_calendar_service()

        event = {
            "summary": summary,
            "location": location,
            "description": description,
            "start": {
                "dateTime": start_time_iso,
                "timeZone": timezone,
            },
            "end": {
                "dateTime": end_time_iso,
                "timeZone": timezone,
            },
        }

        created_event = (
            service.events().insert(calendarId="primary", body=event).execute()
        )
        event_link = created_event.get("htmlLink", "")

        return f"Event '{summary}' successfully created in Google Calendar! Link: {event_link}"

    except Exception as e:
        return f"Failed to create calendar event: {str(e)}"