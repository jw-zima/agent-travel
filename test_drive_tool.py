from tools.drive_tools import create_travel_itinerary_doc

if __name__ == "__main__":
    print("Testing Google Drive & Google Docs Tool...\n")
    
    sample_content = (
        "=== FLIGHT DETAILS ===\n"
        "Option 1: Ryanair | WAW -> FCO | Price: 250 PLN\n"
        "Departure: 2026-09-15 06:00 | Arrival: 2026-09-15 08:30\n\n"
        "=== HOTEL ACCOMMODATION ===\n"
        "Option 1: Hotel Artemide | Rome City Center\n"
        "Price: 1200 PLN total (3 nights) | Rating: 4.8/5.0\n\n"
        "=== STATUS ===\n"
        "Approved by User. Events added to Google Calendar."
    )

    result = create_travel_itinerary_doc(
        folder_name="Travel_Itinerary_Rome_2026",
        doc_title="Rome Weekend Trip Itinerary",
        content_markdown=sample_content
    )

    print("Result Output:")
    print("=" * 60)
    print(result)
    print("=" * 60)