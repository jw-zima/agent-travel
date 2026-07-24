import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import serpapi

# Load environment variables from .env file
load_dotenv()

def validate_hotel_params(q: str, check_in_date: str, check_out_date: str) -> Optional[str]:
    """
    Validates hotel search parameters before executing SerpApi request.
    """
    if not q or not q.strip():
        return "Error: Location query 'q' cannot be empty."

    try:
        check_in_dt = datetime.strptime(check_in_date, "%Y-%m-%d").date()
        if check_in_dt < datetime.now().date():
            return f"Error: Check-in date '{check_in_date}' is in the past. Please specify a future date."
    except ValueError:
        return f"Error: Check-in date '{check_in_date}' has invalid format. Must be YYYY-MM-DD."

    try:
        check_out_dt = datetime.strptime(check_out_date, "%Y-%m-%d").date()
        if check_out_dt <= check_in_dt:
            return f"Error: Check-out date '{check_out_date}' must be later than check-in date '{check_in_date}'."
    except ValueError:
        return f"Error: Check-out date '{check_out_date}' has invalid format. Must be YYYY-MM-DD."

    return None

def search_hotels(
    q: str,
    check_in_date: str,
    check_out_date: str,
    adults: int = 2,
    currency: str = "PLN",
    hl: str = "en"
) -> str:
    """
    Searches for hotels using Google Hotels via SerpApi with input validation.
    """
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key or api_key.strip() == "":
        return "Error: SERPAPI_KEY is missing or empty. Check your .env file."

    # Validate parameters
    validation_error = validate_hotel_params(q, check_in_date, check_out_date)
    if validation_error:
        return validation_error

    params: Dict[str, Any] = {
        "engine": "google_hotels",
        "q": q,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "adults": adults,
        "currency": currency,
        "hl": hl,
        "api_key": api_key
    }

    try:
        client = serpapi.Client(api_key=api_key)
        results = client.search(params)
        results_dict = results.as_dict() if hasattr(results, "as_dict") else dict(results)

        if "error" in results_dict:
            return f"SerpApi Error: {results_dict['error']}"

        properties: List[Dict[str, Any]] = results_dict.get("properties", [])

        if not properties:
            return f"No hotel properties found for query '{q}' from {check_in_date} to {check_out_date}."

        formatted_output = [
            f"### Hotel Search Results for '{q}' ({check_in_date} to {check_out_date})\n"
        ]

        for idx, hotel in enumerate(properties[:5], 1):
            name = hotel.get("name", "Unknown Hotel")
            
            # Robust Price Extraction Logic
            price_str = "N/A"
            rate_per_night = hotel.get("rate_per_night", {})
            if isinstance(rate_per_night, dict):
                price_str = rate_per_night.get("lowest") or rate_per_night.get("extracted") or "N/A"

            if price_str == "N/A":
                total_rate = hotel.get("total_rate", {})
                if isinstance(total_rate, dict):
                    price_str = total_rate.get("lowest") or total_rate.get("extracted") or "N/A"

            if price_str == "N/A" and "prices" in hotel and isinstance(hotel["prices"], list) and len(hotel["prices"]) > 0:
                first_price = hotel["prices"][0]
                price_str = first_price.get("price") or first_price.get("rate_per_night", {}).get("lowest", "N/A")

            price_info = f"{price_str} {currency}" if price_str != "N/A" else "Price unavailable"

            overall_rating = hotel.get("overall_rating", "N/A")
            reviews = hotel.get("reviews", "N/A")
            hotel_class = hotel.get("extracted_hotel_class", "N/A")
            
            amenities = hotel.get("amenities", [])
            amenities_str = ", ".join(amenities[:4]) if amenities else "Standard amenities"

            formatted_output.append(
                f"**Option {idx}: {name}**\n"
                f"  - Price: {price_info}\n"
                f"  - Rating: {overall_rating}/5.0 ({reviews} reviews) | Stars: {hotel_class}\n"
                f"  - Highlights: {amenities_str}\n"
            )

        return "\n".join(formatted_output)

    except Exception as e:
        return f"An exception occurred during hotel search execution: {str(e)}"