from tools.hotel_tools import search_hotels

if __name__ == "__main__":
    print("Testing real Google Hotels integration via SerpApi...\n")
    
    # Test Hotel Search: Rome city center for September 2026
    result = search_hotels(
        q="Rome city center",
        check_in_date="2026-09-15",
        check_out_date="2026-09-18",
        adults=2
    )
    
    print("Hotel Search Result Output:")
    print("=" * 60)
    print(result)
    print("=" * 60)