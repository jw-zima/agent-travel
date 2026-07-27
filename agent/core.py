import os
import re
import time
from typing import Dict, Any, Callable, Optional
from dotenv import load_dotenv

# Import standard official Google GenAI SDK
from google import genai
from google.genai import types
from google.genai.errors import ServerError, APIError

# Import prompts and tools
from agent.prompts import SYSTEM_PROMPT
from tools.flight_tools import search_flights
from tools.hotel_tools import search_hotels
from tools.calendar_tools import add_calendar_event
from tools.drive_tools import create_travel_itinerary_doc

# Load environment variables
load_dotenv()

# Registry mapping tool names as strings to python function references
TOOL_REGISTRY: Dict[str, Callable] = {
    "search_flights": search_flights,
    "search_hotels": search_hotels,
    "add_calendar_event": add_calendar_event,
    "create_travel_itinerary_doc": create_travel_itinerary_doc
}


def extract_trip_context(user_text: str) -> Dict[str, Any]:
    """
    Extracts simple trip metadata from the user query to support round-trip flight handling.
    """
    upper_text = user_text.upper()
    iata_codes = re.findall(r"\b([A-Z]{3})\b", upper_text)

    origin = None
    destination = None
    if len(iata_codes) >= 2:
        origin = iata_codes[0]
        destination = iata_codes[1]

    dates = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", user_text)
    outbound_date = dates[0] if dates else None
    return_date = dates[1] if len(dates) > 1 else None

    is_round_trip = bool(return_date) or any(word in upper_text for word in [" RETURN ", " POWRÓT", " POWROT", " DO "])

    return {
        "origin": origin,
        "destination": destination,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "is_round_trip": is_round_trip,
    }


def execute_flight_search(kwargs: Dict[str, Any], trip_context: Optional[Dict[str, Any]] = None) -> str:
    """
    Executes flight search for both legs when the user requested a round-trip itinerary.
    """
    if trip_context and trip_context.get("is_round_trip"):
        departure_id = kwargs.get("departure_id") or trip_context.get("origin")
        arrival_id = kwargs.get("arrival_id") or trip_context.get("destination")
        outbound_date = kwargs.get("outbound_date") or trip_context.get("outbound_date")
        return_date = kwargs.get("return_date") or trip_context.get("return_date")

        if departure_id and arrival_id and outbound_date and return_date:
            outbound_result = search_flights(
                departure_id=departure_id,
                arrival_id=arrival_id,
                outbound_date=outbound_date,
                currency=kwargs.get("currency", "PLN"),
                hl=kwargs.get("hl", "en")
            )
            return_result = search_flights(
                departure_id=arrival_id,
                arrival_id=departure_id,
                outbound_date=return_date,
                currency=kwargs.get("currency", "PLN"),
                hl=kwargs.get("hl", "en")
            )
            return (
                f"### Round-trip Flight Search Results\n"
                f"Outbound leg ({departure_id} -> {arrival_id} on {outbound_date}):\n{outbound_result}\n\n"
                f"Return leg ({arrival_id} -> {departure_id} on {return_date}):\n{return_result}"
            )

    return search_flights(**kwargs)


def parse_action(llm_text: str):
    """
    Parses 'Action: function_name(arg1="val1", arg2="val2")' from LLM output.
    Returns (func_name, kwargs_dict) or (None, None) if no Action pattern matches.
    """
    pattern = r"Action:\s*([a-zA-Z0-9_]+)\((.*)\)"
    match = re.search(pattern, llm_text)
    if not match:
        return None, None

    func_name = match.group(1).strip()
    args_str = match.group(2).strip()

    kwargs = {}
    if args_str:
        arg_pattern = r'([a-zA-Z0-9_]+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s,]+))'
        for arg_match in re.finditer(arg_pattern, args_str):
            key = arg_match.group(1)
            val = arg_match.group(2) if arg_match.group(2) is not None else (
                arg_match.group(3) if arg_match.group(3) is not None else arg_match.group(4)
            )
            if isinstance(val, str) and val.isdigit():
                val = int(val)
            kwargs[key] = val

    return func_name, kwargs


def send_message_with_retry(chat, prompt: str, max_retries: int = 3, delay: int = 2):
    """
    Sends a message to Gemini API with a strict maximum of 3 retries.
    """
    for attempt in range(1, max_retries + 1):
        try:
            return chat.send_message(prompt)
        except (ServerError, APIError) as e:
            if attempt == max_retries:
                print(f"\n❌ Reached maximum API retries ({max_retries}). Halting call.")
                raise e
            print(f"\n⚠️ Google API busy (ServerError). Retry attempt {attempt}/{max_retries} in {delay}s...")
            time.sleep(delay)
            delay *= 2


def run_react_agent(user_prompt: str, max_iterations: int = 10):
    """
    Main ReAct loop with max retries limit (3) and repeated action detection to prevent infinite loops.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is not set in .env")
        return

    client = genai.Client(api_key=api_key)

    chat = client.chats.create(
        model="gemini-3.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.1
        )
    )

    current_input = user_prompt
    iteration = 0
    trip_context = extract_trip_context(user_prompt)

    # Tracking tools calls to prevent infinite loops
    last_action_signature = None
    action_repeat_count = 0
    MAX_ACTION_REPEATS = 3

    print(f"\n🚀 Starting Travel Agent ReAct Session...")
    print(f"User Request: {user_prompt}\n" + "="*60)

    tool_registry: Dict[str, Callable] = {
        "search_flights": lambda **kwargs: execute_flight_search(kwargs, trip_context),
        "search_hotels": search_hotels,
        "add_calendar_event": add_calendar_event,
        "create_travel_itinerary_doc": create_travel_itinerary_doc,
    }

    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- [Iteration {iteration}] ---")
        
        # Call LLM with max 3 retries limit
        response = send_message_with_retry(chat, current_input, max_retries=3)
        response_text = response.text
        print(f"\n🤖 Agent Output:\n{response_text}")

        # Check Human-In-The-Loop Checkpoint
        if "STATUS: PENDING_APPROVAL" in response_text:
            print("\n⏸️  [HUMAN-IN-THE-LOOP CHECKPOINT]")
            user_approval = input("👉 Enter your input/approval for the Agent: ").strip()
            current_input = f"User Response: {user_approval}"
            # Reset repeat tracker after human interaction
            action_repeat_count = 0
            last_action_signature = None
            continue

        func_name, kwargs = parse_action(response_text)

        if func_name:
            action_signature = f"{func_name}:{str(sorted(kwargs.items()))}"
            if action_signature == last_action_signature:
                action_repeat_count += 1
            else:
                last_action_signature = action_signature
                action_repeat_count = 1

            if action_repeat_count >= MAX_ACTION_REPEATS:
                error_msg = f"Error: Action '{func_name}' was attempted {action_repeat_count} times repeatedly without progress. Halting loop to prevent infinite repetition."
                print(f"\n⛔ {error_msg}")
                break

            if func_name in tool_registry:
                print(f"\n⚙️ Executing Tool: `{func_name}` with args: {kwargs}")
                tool_func = tool_registry[func_name]
                
                try:
                    tool_result = tool_func(**kwargs)
                except Exception as e:
                    tool_result = f"Error executing tool {func_name}: {str(e)}"

                print(f"\n👁️ Tool Observation:\n{tool_result}")
                current_input = f"Observation: {tool_result}"
            else:
                available_tools = ", ".join(tool_registry.keys())
                error_msg = f"Error: Tool '{func_name}' is not recognized. Available tools are: [{available_tools}]."
                print(f"\n⚠️ {error_msg}")
                current_input = f"Observation: {error_msg}"
        else:
            print("\n✅ Execution Finished or Awaiting Final Input.")
            break

    if iteration >= max_iterations:
        print("\n⚠️ Maximum iterations reached without final resolution.")