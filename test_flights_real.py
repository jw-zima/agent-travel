from tools.flight_tools import search_flights

if __name__ == "__main__":
    print("Testing real Google Flights integration via SerpApi...\n")
    
    # Test One-Way Flight Search: Warsaw (WAW) to Rome (FCO)
    result = search_flights(
        departure_id="WAW",
        arrival_id="FCO",
        outbound_date="2026-11-15"
    )
    
    print("Search Result Output:")
    print("=" * 60)
    print(result)
    print("=" * 60)