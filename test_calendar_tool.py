from tools.calendar_tools import add_calendar_event

# Test adding a sample flight event
result = add_calendar_event(
    summary="Flight to Rome (TEST)",
    location="Chopin Airport -> Fiumicino Airport",
    description="Booking ref: ABC123XYZ. Departure: 10:00 AM.",
    start_time_iso="2026-09-10T10:00:00",
    end_time_iso="2026-09-10T12:30:00",
)

print(result)