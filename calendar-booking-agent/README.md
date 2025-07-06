# Calendar Booking Agent

A conversational AI agent that helps users book appointments on Google Calendar through natural chat interactions.

## Features

- Natural language conversation for appointment booking
- Google Calendar integration with availability checking
- Alternative slot suggestions when requested time is unavailable
- Built with FastAPI backend and Streamlit frontend
- Powered by Google's Gemini LLM with LangChain

## Tech Stack

- **Backend**: Python + FastAPI
- **Agent Framework**: LangChain with function/tool-calling
- **Calendar Integration**: Google Calendar API via Service Account
- **Frontend**: Streamlit chat interface
- **LLM**: Google Gemini

## Project Structure

```
calendar-booking-agent/
├── backend/
│   ├── app.py              # FastAPI application
│   ├── calendar_client.py  # Google Calendar integration
│   ├── agent.py           # LangChain agent with calendar tools
│   ├── config.py          # Configuration management
│   └── requirements.txt   # Backend dependencies
├── frontend/
│   ├── app.py             # Streamlit chat interface
│   └── requirements.txt   # Frontend dependencies
└── docs/
    └── setup.md           # Detailed setup instructions
```

## Quick Start

### Prerequisites

1. Google Cloud Project with Calendar API enabled
2. Service Account with calendar access
3. Python 3.9+

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Set environment variables
export GOOGLE_CALENDAR_CREDENTIALS_PATH="path/to/service-account-key.json"
export GOOGLE_CALENDAR_ID="your-calendar-id@group.calendar.google.com"
export GOOGLE_API_KEY="your-gemini-api-key"

# Run the backend
uvicorn app:app --reload
```

### Frontend Setup

```bash
cd frontend
pip install -r requirements.txt

# Set backend URL
export BACKEND_URL="http://localhost:8000"

# Run the frontend
streamlit run app.py
```

## Usage

1. Start the backend server
2. Launch the Streamlit frontend
3. Begin chatting with the agent to book appointments
4. The agent will:
   - Understand your booking request
   - Check calendar availability
   - Suggest alternative slots if needed
   - Confirm and create the appointment

## Environment Variables

### Backend
- `GOOGLE_CALENDAR_CREDENTIALS_PATH`: Path to service account JSON key
- `GOOGLE_CALENDAR_ID`: Google Calendar ID
- `GOOGLE_API_KEY`: Google Gemini API key
- `PORT`: Server port (default: 8000)

### Frontend
- `BACKEND_URL`: Backend API URL

## API Endpoints

- `POST /chat`: Send messages to the booking agent
- `GET /health`: Health check endpoint

## Development

See [docs/setup.md](docs/setup.md) for detailed setup instructions including Google Cloud configuration.

## License

MIT