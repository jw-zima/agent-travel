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

## TO BE CONTINUED