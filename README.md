# ScheduleAI - Conversational Calendar Booking Agent ✅ **FULLY WORKING**

A complete conversational agent that enables **real calendar booking** through natural language chat with Google Calendar integration. Built with FastAPI, LangChain, Gemini AI, and Streamlit.

## 🎉 **Current Status: PRODUCTION READY**

- ✅ **Real Calendar Integration** - Actually reads and writes to Google Calendar
- ✅ **Intelligent Agent** - LangChain agent with tool calling capabilities  
- ✅ **Natural Language** - Book meetings with conversational commands
- ✅ **Smart Scheduling** - Finds available slots and avoids conflicts
- ✅ **Modern UI** - Responsive Streamlit chat interface

## 🚀 Features

### **Real Calendar Functionality**
- **Availability Checking**: Reads your actual Google Calendar for conflicts
- **Event Creation**: Creates real calendar events with proper details
- **Smart Scheduling**: Finds gaps between existing meetings
- **Alternative Suggestions**: Offers other times when requested slots are busy
- **Conflict Prevention**: Avoids double-booking automatically

### **Intelligent Conversation**
- **Natural Language**: "Book a team meeting tomorrow at 2 PM"
- **Date Understanding**: Parses "tomorrow", "next Friday", "in 2 hours"
- **Context Awareness**: Remembers conversation history
- **Clarification**: Asks for missing details (duration, title, etc.)
- **Confirmation**: Verifies details before creating events

### **Technical Excellence**
- **LangChain Agent**: Function-calling with custom calendar tools
- **Gemini AI**: Powered by Google's latest LLM
- **FastAPI Backend**: High-performance async API
- **Streamlit Frontend**: Modern chat interface
- **Error Handling**: Graceful fallbacks and helpful messages

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/JSON    ┌─────────────────┐
│   Streamlit     │◄───────────────►│   FastAPI       │
│   Frontend      │                 │   Backend       │
│   (Port 8501)   │                 │   (Port 8000)   │
└─────────────────┘                 └─────────────────┘
                                            │
                                            ▼
                                    ┌─────────────────┐
                                    │   LangChain     │
                                    │   Agent         │
                                    │   + Tools       │
                                    └─────────────────┘
                                            │
                                            ▼
                                    ┌─────────────────┐
                                    │  Google APIs    │
                                    │  • Gemini AI    │
                                    │  • Calendar API │
                                    └─────────────────┘
```

## 📁 Project Structure

```
ScheduleAI/
├── backend/                 # FastAPI Backend
│   ├── main.py             # API endpoints
│   ├── booking_agent.py    # LangChain agent
│   ├── agent_tools.py      # Calendar tools
│   ├── calendar_client.py  # Google Calendar integration
│   └── __init__.py
├── frontend/               # Streamlit Frontend  
│   └── app.py             # Chat interface
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── start_backend.sh       # Backend startup script
├── start_frontend.sh      # Frontend startup script
├── SETUP_GUIDE.md         # Detailed setup instructions
└── README.md             # This file
```

## 🚀 Quick Start

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Get Google API Key** (Required)
1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create an API key
3. Add to `.env` file:
```bash
cp .env.example .env
# Edit .env and add your API key
GOOGLE_API_KEY=your_actual_api_key_here
```

### 3. **Start the Applications**
```bash
# Start backend (Terminal 1)
./start_backend.sh

# Start frontend (Terminal 2)  
./start_frontend.sh
```

### 4. **Open and Test**
- **Frontend**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 💬 Example Usage

**You:** "I need to schedule a team meeting for tomorrow at 2 PM"

**Agent:** "Let me check your calendar availability for tomorrow at 2 PM..."
*[Uses check_availability tool]*
"Great! I found that time slot is available. What would you like to call this meeting, and how long should it be?"

**You:** "Make it a 'Weekly Team Sync' for 1 hour"

**Agent:** "Perfect! I'll create a 'Weekly Team Sync' meeting for tomorrow from 2:00 PM to 3:00 PM."
*[Uses create_calendar_event tool]*
"✅ Meeting created successfully! I've added it to your calendar."

## 🔧 Advanced Setup (Optional)

For **real Google Calendar integration** (vs. mock data), see [SETUP_GUIDE.md](SETUP_GUIDE.md) for:
- Google Cloud Project setup
- Calendar API configuration  
- Service account creation
- Calendar sharing permissions

**Note**: The system works with mock data if you only have the Gemini API key!

## 🧪 Testing

### Backend Health
```bash
curl http://localhost:8000/health
```

### Calendar Integration Test
```bash
curl http://localhost:8000/test-calendar
```

### Chat Test
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Check my availability for tomorrow"}'
```

## 🛠️ What's Fixed

### ✅ **Real Agent Functionality**
- Replaced hardcoded responses with actual LangChain agent
- Integrated real calendar tools (availability, event creation)
- Added proper error handling and fallbacks

### ✅ **Calendar Integration**
- Working Google Calendar API client
- Real availability checking vs. mock data
- Actual event creation with proper formatting

### ✅ **Smart Features**
- Natural date parsing ("tomorrow", "next week")
- Context-aware conversations
- Alternative time suggestions
- Confirmation workflows

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| Agent not available | Add valid Google API key to `.env` |
| Backend won't start | Check Python dependencies: `pip install -r requirements.txt` |
| Frontend connection error | Ensure backend is running on port 8000 |
| Calendar not working | System uses mock data without service account setup |

## 📚 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup instructions
- **[.env.example](.env.example)** - Environment configuration template
- **Backend API** - Auto-generated docs at http://localhost:8000/docs

## 🎯 Key Components

### **Backend (FastAPI)**
- **main.py**: API endpoints with real agent integration
- **booking_agent.py**: LangChain agent with Gemini LLM
- **agent_tools.py**: Custom tools for calendar operations
- **calendar_client.py**: Google Calendar API client

### **Frontend (Streamlit)**
- **app.py**: Modern chat interface with real-time responses

### **Agent Tools**
- `check_availability`: Reads real calendar, finds free slots
- `create_calendar_event`: Creates actual calendar events
- `get_busy_times`: Shows existing calendar conflicts

## 🎉 Success! 

The ScheduleAI system is now **fully functional** with:
- ✅ Real calendar booking capabilities
- ✅ Intelligent conversation handling  
- ✅ Modern web interface
- ✅ Production-ready architecture

**Ready to schedule your first meeting?** 🚀

---

## 🤝 Contributing

Feel free to open issues or submit PRs to improve the calendar booking experience!

## � License

MIT License - Feel free to use this for your own calendar booking needs!
