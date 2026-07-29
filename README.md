# ✈️ AI Travel Agent – ReAct Loop with Google Workspace & SerpApi

An autonomous AI Travel Assistant built with the official **Google GenAI SDK** (`google-genai`). The agent executes a **ReAct (Reasoning & Acting)** loop to search for real-time flights and hotels, manage Human-In-The-Loop (HITL) approval checkpoints, and automatically export approved travel itineraries to **Google Calendar** and **Google Drive**.

---

## 🏗️ Architecture & Features

- **ReAct Orchestration Loop**: Native Python implementation executing `Thought -> Action -> Observation` cycles with built-in reflection, self-correction, and circuit breakers against infinite loops.
- **Intent-Aware Search Routing**: The agent can distinguish whether the user wants flights only, hotels only, or both, and it will constrain tool use accordingly.
- **Real-Time Search Integrations**:
  - **Google Flights API** (via SerpApi): Finds flight options with IATA airport validation and round-trip support.
  - **Google Hotels API** (via SerpApi): Searches accommodation options with fallback price extraction and rating filters.
- **Google Workspace Integration (OAuth 2.0)**:
  - **Google Calendar**: Creates travel booking events upon explicit approval.
  - **Google Drive & Google Docs**: Generates structured travel itinerary report documents.
- **Safety & Guardrails**:
  - **Two-Phase Human-In-The-Loop (HITL)**: Requires explicit user approval at key checkpoints (`PENDING_APPROVAL`) before making hotel searches or calendar/doc entries.
  - **API Rate Control & Retry Logic**: Handles temporary Google API busy states (503/Server Errors) with exponential backoff.
  - **Input Validation**: Enforces valid IATA airport codes and future date formats (`YYYY-MM-DD`).

---

## 📂 Project Structure

```text
agent-travel/
├── agent/
│   ├── __init__.py
│   ├── core.py             # ReAct loop orchestrator & execution engine
│   └── prompts.py          # System prompts, ReAct rules & HITL workflow definitions
├── tools/
│   ├── __init__.py
│   ├── flight_tools.py     # SerpApi Google Flights search tool & validation
│   ├── hotel_tools.py      # SerpApi Google Hotels search tool & price fallback
│   ├── calendar_tools.py   # Google Calendar API event creation
│   └── drive_tools.py      # Google Drive & Docs API itinerary exporter
├── .env.example            # Environment variables template
├── environment.yml         # Conda environment configuration file
├── setup_oauth.py          # Interactive OAuth 2.0 credential setup script
├── main.py                 # Interactive terminal application entry point
├── test_trip_intent_routing.py  # Tests for flight-only / hotel-only / both routing
└── README.md               # Project documentation
```

## 🚀 Getting Started

### 1. Prerequisites & Environment Setup
Clone the repository and create the Conda environment using `environment.yml`:

> git clone https://github.com/YOUR_USERNAME/agent-travel.git
>
> cd agent-travel
>
> conda env create -f environment.yml
>
> conda activate agent_travel

### 2. Configure API Keys
Create a `.env` file in the root directory by copying `.env.example`:

> cp .env.example .env
Fill in your actual secret keys inside `.env`:

- `GEMINI_API_KEY` = your_google_ai_studio_api_key
- `SERPAPI_KEY` = your_serpapi_key

### 3. Install Test Dependencies
If you want to run the included routing tests locally, make sure pytest is available in the environment:

> conda env update -f environment.yml

### 4. Setup Google Workspace OAuth 2.0

1. Download your OAuth 2.0 Client Credentials JSON from the Google Cloud Console.
2. Save the file in the project root directory as **`credentials.json`**.
3. Run the interactive authentication setup script:

> python setup_oauth.py
This will open your browser to authorize access for Google Calendar, Google Drive, and Google Docs, generating a local **`token.json`** file.

## 🧪 Usage & Example Run
Run the main application:

> python main.py

### Example Interactive Flow

1. **User Query**: "Find me flights from Warsaw (WAW) to Rome (FCO) on 2026-09-15."
2. **Flight-only mode**: The agent focuses only on flight search and does not invoke hotel tools.
3. **User Query**: "Find me hotels in Rome from 2026-09-15 to 2026-09-18."
4. **Hotel-only mode**: The agent focuses only on accommodations and skips flight search.
5. **User Query**: "Find me flights and hotels for Warsaw to Rome from 2026-09-15 to 2026-09-18."
6. **Combined mode**: The agent searches flights first, pauses for approval, and then proceeds to hotels if approved.

### Running Tests

> pytest -q test_trip_intent_routing.py

## 🛡️ License & Disclaimer
**Disclaimer**: This project is for planning and educational purposes. The AI agent **does not perform actual financial bookings or payment transactions**. All saved calendar and drive items are strictly informative context entries.