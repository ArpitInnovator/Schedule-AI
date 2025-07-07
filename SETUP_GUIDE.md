# ScheduleAI - Setup Guide for Real Calendar Integration

## 🚀 Quick Start

The system is now **fully functional** with real calendar booking capabilities! Follow these steps to get it working with your Google Calendar.

## 📋 Prerequisites

1. **Python 3.8+** (Python 3.13 recommended)
2. **Google Cloud Project** (for Calendar API access)
3. **Google AI Studio Account** (for Gemini API key)

## 🔧 Step 1: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

## 🗝️ Step 2: Get Google API Key (Required)

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create a new API key
3. Copy your API key

## 📅 Step 3: Set Up Google Calendar (Optional but Recommended)

### For Real Calendar Integration:

1. **Create Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Calendar API:**
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

3. **Create Service Account:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in details and create
   - Click on the created service account
   - Go to "Keys" tab > "Add Key" > "Create New Key" > "JSON"
   - Download the JSON file

4. **Share Calendar with Service Account:**
   - Open Google Calendar
   - Go to calendar settings
   - Share with the service account email (from JSON file)
   - Give "Make changes and manage sharing" permission

## ⚙️ Step 4: Configure Environment

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file with your credentials:**
   ```bash
   # Required - Get from https://aistudio.google.com/apikey
   GOOGLE_API_KEY=your_actual_google_ai_api_key
   
   # Optional - For real calendar integration
   GOOGLE_SERVICE_ACCOUNT_JSON={"type": "service_account", ...}
   GOOGLE_CALENDAR_ID=primary
   ```

## 🎯 Step 5: Run the Application

### Start Backend:
```bash
# Method 1: Using the script
./start_backend.sh

# Method 2: Manual
cd backend
python main.py
```

### Start Frontend:
```bash
# Method 1: Using the script  
./start_frontend.sh

# Method 2: Manual
cd frontend
streamlit run app.py
```

## 🧪 Step 6: Test the System

1. **Check Backend Health:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test Calendar Integration:**
   ```bash
   curl http://localhost:8000/test-calendar
   ```

3. **Open Frontend:**
   - Go to http://localhost:8501
   - Try booking a meeting!

## 🎉 What Works Now

### ✅ **Real Calendar Functionality:**
- **Actual availability checking** - Reads your real Google Calendar
- **Smart scheduling** - Finds gaps between existing events
- **Real event creation** - Creates actual calendar events
- **Conflict detection** - Avoids double-booking

### ✅ **Intelligent Agent Features:**
- **Natural language processing** - "Book a team meeting tomorrow at 2 PM"
- **Date parsing** - Understands "tomorrow", "next Friday", etc.
- **Alternative suggestions** - Offers other times if requested slot is busy
- **Context awareness** - Remembers conversation history

### ✅ **Mock Mode (No Calendar Setup):**
- If you only have the Gemini API key, the system works with **mock data**
- Perfect for testing and demonstration
- All features work except real calendar integration

## 💬 Example Conversations

**User:** "I need to schedule a team meeting for tomorrow at 2 PM"

**Agent:** 
1. Checks your real calendar for conflicts
2. If available: "I found that time slot is free! What should I call this meeting?"
3. If busy: "That time is already booked. I found these alternatives: [lists actual available times]"
4. Creates the actual calendar event after confirmation

**User:** "Check my availability for next Monday"

**Agent:** Shows your real busy times and suggests available slots

## 🔍 Troubleshooting

### Agent Not Available
- **Check:** Google API key is set correctly
- **Fix:** Get a valid API key from Google AI Studio

### Calendar Features Not Working
- **Check:** Service account JSON is configured
- **Check:** Calendar is shared with service account email
- **Note:** System works with mock data if calendar isn't configured

### Backend Connection Issues
- **Check:** Backend is running on port 8000
- **Fix:** Run `python backend/main.py`

### Frontend Not Loading
- **Check:** Frontend is running on port 8501  
- **Fix:** Run `streamlit run frontend/app.py`

## 📚 Advanced Configuration

### Custom Calendar ID
```bash
# Use specific calendar instead of primary
GOOGLE_CALENDAR_ID=your-calendar-id@group.calendar.google.com
```

### Business Hours Customization
Edit `backend/calendar_client.py` to modify business hours logic.

### Agent Behavior
Edit `backend/booking_agent.py` to customize agent prompts and behavior.

## 🚦 System Status

- ✅ **Backend**: Fully functional with LangChain agent
- ✅ **Frontend**: Connected and responsive  
- ✅ **Calendar Integration**: Working with mock/real data
- ✅ **Agent Tools**: Availability checking, event creation
- ✅ **Error Handling**: Graceful fallbacks and helpful messages

## 🎯 Next Steps

1. **Add your Google API key** to `.env` file
2. **Optionally set up Calendar API** for real integration
3. **Start both backend and frontend**
4. **Test with real booking requests**

The system is now **production-ready** for real calendar booking! 🎉