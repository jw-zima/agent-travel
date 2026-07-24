import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import serpapi

# Load environment variables from .env file
load_dotenv()

def validate_flight_params(departure_id: str, arrival_id: str, outbound_date: str, return_date: Optional[str] = None) -> Optional[str]:
    """
    Validates input arguments before calling Google Flights API.
    Returns error message string if invalid, or None if validation passes.
    """
    # 1. Validate IATA codes (exactly 3 uppercase letters)
    dep = departure_id.strip().upper()
    arr = arrival_id.strip().upper()
    if not re.match(r"^[A-Z]{3}$", dep):
        return f"Error: Departure airport code '{departure_id}' is invalid. Must be a 3-letter IATA code (e.g. WAW)."
    if not re.match(r"^[A-Z]{3}$", arr):
        return f"Error: Arrival airport code '{arrival_id}' is invalid. Must be a 3-letter IATA code (e.g. FCO)."

    # 2. Validate outbound_date format (YYYY-MM-DD) and check it's not in the past
    try:
        outbound_dt = datetime.strptime(outbound_date, "%Y-%m-%d").date()
        if outbound_dt < datetime.now().date():
            return f"Error: Outbound date '{outbound_date}' is in the past. Please specify a future date."
    except ValueError:
        return f"Error: Outbound date '{outbound_date}' has invalid format. Must be YYYY-MM-DD."

    # 3. Validate return_date if provided
    if return_date:
        try:
            return_dt = datetime.strptime(return_date, "%Y-%m-%d").date()
            if return_dt < outbound_dt:
                return f"Error: Return date '{return_date}' cannot be earlier than outbound date '{outbound_date}'."
        except ValueError:
            return f"Error: Return date '{return_date}' has invalid format. Must be YYYY-MM-DD."

    return None

def search_flights(
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    return_date: str = None,
    currency: str = "PLN",
    hl: str = "en"
) -> str:
    """
    Searches for flights using Google Flights via SerpApi with input validation.
    """
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key or api_key.strip() == "":
        return "Error: SERPAPI_KEY is missing or empty. Check your .env file."

    # Run parameter validation
    validation_error = validate_flight_params(departure_id, arrival_id, outbound_date, return_date)
    if validation_error:
        return validation_error

    dep_id = departure_id.strip().upper()
    arr_id = arrival_id.strip().upper()

    params: Dict[str, Any] = {
        "engine": "google_flights",
        "departure_id": dep_id,
        "arrival_id": arr_id,
        "outbound_date": outbound_date,
        "currency": currency,
        "hl": hl,
        "api_key": api_key
    }

    if return_date:
        params["return_date"] = return_date
        params["type"] = "1"  # Round trip
    else:
        params["type"] = "2"  # One way

    try:
        client = serpapi.Client(api_key=api_key)
        results = client.search(params)
        results_dict = results.as_dict() if hasattr(results, "as_dict") else dict(results)

        if "error" in results_dict:
            return f"SerpApi Error: {results_dict['error']}"

        best_flights: List[Dict[str, Any]] = results_dict.get("best_flights", [])
        other_flights: List[Dict[str, Any]] = results_dict.get("other_flights", [])
        
        all_flights = best_flights + other_flights

        if not all_flights:
            return f"No flights found from {dep_id} to {arr_id} on {outbound_date}."

        formatted_output = [f"### Flight Search Results: {dep_id} -> {arr_id} ({outbound_date})\n"]

        for idx, flight_option in enumerate(all_flights[:5], 1):
            price = flight_option.get("price", "N/A")
            total_duration = flight_option.get("total_duration", "N/A")
            
            flights_info = []
            for flight in flight_option.get("flights", []):
                airline = flight.get("airline", "Unknown Airline")
                flight_number = flight.get("flight_number", "")
                dep_airport = flight.get("departure_airport", {}).get("name", "N/A")
                dep_time = flight.get("departure_airport", {}).get("time", "N/A")
                arr_airport = flight.get("arrival_airport", {}).get("name", "N/A")
                arr_time = flight.get("arrival_airport", {}).get("time", "N/A")
                
                flights_info.append(
                    f"  - {airline} ({flight_number}): {dep_airport} [{dep_time}] -> {arr_airport} [{arr_time}]"
                )

            flight_details = "\n".join(flights_info)
            formatted_output.append(
                f"**Option {idx}** | Price: {price} {currency} | Total Duration: {total_duration} mins\n"
                f"{flight_details}\n"
            )

        return "\n".join(formatted_output)

    except Exception as e:
        return f"An exception occurred during flight search execution: {str(e)}"