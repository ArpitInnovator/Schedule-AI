# ScheduleAI - Conversational Calendar Booking Agent

A full-stack conversational agent that enables natural language calendar booking through Google Calendar integration. Built with FastAPI, LangChain, Gemini AI, and Streamlit.

## 🚀 Features

- **Natural Language Processing**: Book appointments using conversational language
- **Google Calendar Integration**: Real-time availability checking and event creation
- **Intelligent Scheduling**: Suggests alternative time slots when requested times are unavailable
- **Interactive Chat Interface**: Modern Streamlit-based UI with real-time conversation
- **Function Calling**: LangChain agent with tool-calling capabilities
- **Flexible Configuration**: Easy setup with environment variables

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/JSON    ┌─────────────────┐
│                 │                 │                 │
│   Streamlit     │◄───────────────►│   FastAPI       │
│   Frontend      │                 │   Backend       │
│                 │                 │                 │
└─────────────────┘                 └─────────────────┘
                                            │
                                            │
                                    ┌───────▼────────┐
                                    │                │
                                    │   LangChain    │
                                    │   Agent        │
                                    │   (Gemini)     │
                                    │                │
                                    └───────┬────────┘
                                            │
                                            │
                                    ┌───────▼────────┐
                                    │                │
                                    │ Google Calendar│
                                    │      API       │
                                    │                │
                                    └────────────────┘
```

### Components

1. **Frontend** (`frontend/app.py`): Streamlit chat interface
2. **Backend** (`backend/main.py`): FastAPI server with chat endpoints
3. **Calendar Client** (`backend/calendar_client.py`): Google Calendar API integration
4. **Agent Tools** (`backend/agent_tools.py`): LangChain tools for calendar operations
5. **Booking Agent** (`backend/booking_agent.py`): Main LangChain agent with Gemini LLM

## 📋 Prerequisites

- Python 3.8+
- Google Cloud Project with Calendar API enabled
- Google API key for Gemini
- Service Account with Calendar access

## ⚙️ Setup Instructions

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd scheduleai
pip install -r requirements.txt
```

### 2. Google Cloud Setup

#### Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable the Google Calendar API

#### Get Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key for configuration

#### Create Service Account
1. In Google Cloud Console, go to "IAM & Admin" > "Service Accounts"
2. Create a new service account
3. Download the JSON key file
4. Share your Google Calendar with the service account email (with "Make changes to events" permission)

### 3. Environment Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Google API Configuration
GOOGLE_API_KEY=your_actual_gemini_api_key

# Google Calendar Service Account (JSON content as a single line string)
GOOGLE_SERVICE_ACCOUNT_JSON={"type": "service_account", "project_id": "your-project", "private_key_id": "...", "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n", "client_email": "...", "client_id": "...", "auth_uri": "...", "token_uri": "...", "auth_provider_x509_cert_url": "...", "client_x509_cert_url": "..."}

# Google Calendar ID (your email or 'primary')
GOOGLE_CALENDAR_ID=your-email@gmail.com
```

**Important**: The service account JSON should be on a single line with escaped quotes.

### 4. Run the Application

#### Start the Backend (Terminal 1)
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Start the Frontend (Terminal 2)
```bash
cd frontend
streamlit run app.py --server.port 8501
```

## 🎯 Usage

### Access the Application
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Example Conversations

```
User: "Schedule a meeting tomorrow at 2 PM"
Assistant: I'll check your availability for tomorrow at 2 PM...

User: "What's my availability next week?"
Assistant: Let me check your calendar for next week...

User: "Book a 30-minute call with John on Friday"
Assistant: I'll look for a 30-minute slot on Friday. What would you like to call this meeting?
```

### Quick Actions
The sidebar includes quick action buttons for common requests:
- Schedule a meeting tomorrow at 2 PM
- Check my availability this week
- Book a 30-minute call on Friday
- Find time for a team meeting next week

## 🔧 API Endpoints

### Backend API Endpoints

- `GET /`: API information
- `GET /health`: System health check
- `POST /chat`: Main chat endpoint
- `GET /greeting`: Get greeting message
- `POST /test-calendar`: Test calendar connection

### Example API Usage

```bash
# Check system health
curl http://localhost:8000/health

# Send a chat message
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Schedule a meeting tomorrow at 2 PM", "chat_history": []}'
```

## 🛠️ Development

### Project Structure

```
scheduleai/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── calendar_client.py   # Google Calendar integration
│   ├── agent_tools.py       # LangChain tools
│   └── booking_agent.py     # Main agent logic
├── frontend/
│   └── app.py              # Streamlit application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
└── README.md             # This file
```

### Adding New Features

1. **New Calendar Operations**: Add methods to `CalendarClient`
2. **New Agent Tools**: Create tools in `agent_tools.py`
3. **UI Enhancements**: Modify `frontend/app.py`
4. **API Endpoints**: Add routes to `backend/main.py`

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Gemini API key | Yes |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Service account credentials (JSON string) | Yes |
| `GOOGLE_CALENDAR_ID` | Target calendar ID | Yes |

## 🧪 Testing

### Manual Testing
1. Start both backend and frontend
2. Open http://localhost:8501
3. Try example conversations
4. Check calendar for created events

### API Testing
```bash
# Test backend health
curl http://localhost:8000/health

# Test calendar connection
curl -X POST http://localhost:8000/test-calendar
```

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Use secure environment variable management
2. **CORS Configuration**: Update allowed origins in `backend/main.py`
3. **Backend URL**: Update `BACKEND_URL` in `frontend/app.py`
4. **Security**: Implement authentication for production use
5. **Scaling**: Consider containerization with Docker

### Docker Deployment (Optional)

Create `Dockerfile` for containerized deployment:

```dockerfile
# Backend
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ ./backend/
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔐 Security Notes

- Store service account JSON securely
- Use environment variables, never commit credentials
- In production, implement proper authentication
- Consider using Google Cloud Secret Manager for credentials

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Troubleshooting

### Common Issues

1. **"Agent not available"**: Check environment variables and backend logs
2. **Calendar connection fails**: Verify service account permissions
3. **Frontend can't reach backend**: Ensure backend is running on port 8000
4. **Import errors**: Run `pip install -r requirements.txt`

### Getting Help

- Check the `/health` endpoint for system status
- Review backend logs for detailed error messages
- Ensure all environment variables are properly set
- Verify Google Calendar API is enabled in your project

## 📧 Support

For issues and questions, please check the troubleshooting section or create an issue in the repository.
