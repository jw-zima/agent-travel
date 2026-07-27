# ✈️ AI Travel Agent – ReAct Loop with Google Workspace & SerpApi

An autonomous AI Travel Assistant built with the official **Google GenAI SDK** (`google-genai`). The agent executes a **ReAct (Reasoning & Acting)** loop to search for real-time flights and hotels, manage Human-In-The-Loop (HITL) approval checkpoints, and automatically export approved travel itineraries to **Google Calendar** and **Google Drive**.

---

## 🏗️ Architecture & Features

- **ReAct Orchestration Loop**: Native Python implementation executing `Thought -> Action -> Observation` cycles with built-in reflection, self-correction, and circuit breakers against infinite loops.
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

### 3. Setup Google Workspace OAuth 2.0

1. Download your OAuth 2.0 Client Credentials JSON from the Google Cloud Console.
2. Save the file in the project root directory as **`credentials.json`**.
3. Run the interactive authentication setup script:

> python setup_oauth.py
This will open your browser to authorize access for Google Calendar, Google Drive, and Google Docs, generating a local **`token.json`** file.

## 🧪 Usage & Example Run
Run the main application:

> python main.py

### Example Interactive Flow

1. **User Query**: "I want to plan a trip from Warsaw (WAW) to Rome (FCO) for the dates from 2026-09-15 to 2026-09-18."
2. **Phase 1 (Flight Search)**: Agent searches flights via SerpApi and halts with status `STATUS: PENDING_APPROVAL`.
3. **User Input**: "Option 1"
4. **Phase 2 (Hotel Search)**: Agent searches hotels for Rome city center and requests final approval (`STATUS: PENDING_APPROVAL`).
5. **User Input**: "Approved"
6. **Phase 3 (Workspace Export)**: Agent creates Calendar events and exports the final Google Doc to Google Drive.

## 🛡️ License & Disclaimer
**Disclaimer**: This project is for planning and educational purposes. The AI agent **does not perform actual financial bookings or payment transactions**. All saved calendar and drive items are strictly informative context entries.