# Schedule AI - Appointment Booking System

A complete AI-powered appointment booking system with a FastAPI backend and Streamlit frontend.

## Features ✨

- **Smart AI Agent**: Understands natural language requests for booking appointments
- **Dynamic Time Slots**: Fetches real available time slots from the backend
- **Real Appointment Booking**: Actually books appointments and tracks them
- **Interactive UI**: Clean Streamlit interface for easy scheduling
- **RESTful API**: FastAPI backend with proper endpoints

## Fixed Issues 🔧

This system has been corrected to address the following problems:
- ✅ **Appointment booking now works** - Replaced stub with real API integration
- ✅ **Shows actual available time slots** - Dynamic fetching from backend calendar
- ✅ **AI agent responds properly** - Real conversation handling for scheduling requests

## Setup & Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start both services:**
   ```bash
   python start_services.py
   ```

   This will start:
   - Backend API server on `http://localhost:8000`
   - Frontend UI on `http://localhost:8501`

3. **Or start services manually:**
   
   **Backend (Terminal 1):**
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   **Frontend (Terminal 2):**
   ```bash
   streamlit run frontend/app.py --server.port 8501
   ```

## Usage 📅

1. **Open the app** at `http://localhost:8501`
2. **Chat with the AI agent** using natural language:
   - "I need to book an appointment"
   - "What times are available?"
   - "Schedule a meeting for tomorrow"
3. **Click on available time slots** to select them
4. **Fill out the booking form** with meeting details
5. **Confirm your appointment** and get a confirmation ID

## API Endpoints 🔌

The backend provides these endpoints:

- `GET /available-slots` - Get all available time slots
- `POST /book-appointment` - Book a new appointment
- `POST /chat` - Chat with the AI scheduling agent
- `GET /appointments` - View all appointments
- `GET /appointments/{id}` - Get specific appointment

## Architecture 🏗️

- **Frontend**: Streamlit app (`frontend/app.py`)
- **Backend**: FastAPI server (`backend/main.py`)
- **Data**: In-memory storage (replace with database for production)
- **AI Agent**: Rule-based conversation handler (can be upgraded to LLM)

## Next Steps 🚀

For production use, consider:
- Integrating with real calendar services (Google Calendar, Outlook)
- Adding user authentication and authorization
- Using a proper database (PostgreSQL, MongoDB)
- Implementing email notifications
- Upgrading to a real LLM for the AI agent (OpenAI, Anthropic)
- Adding appointment cancellation and rescheduling
