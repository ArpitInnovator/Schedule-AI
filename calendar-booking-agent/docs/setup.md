# Detailed Setup Guide

This guide walks you through setting up the Calendar Booking Agent from scratch, including Google Cloud configuration, service account setup, and deployment.

## Prerequisites

- Python 3.9 or higher
- Google Cloud account
- A Google Calendar (can use your personal calendar or create a new one)

## Step 1: Google Cloud Project Setup

### 1.1 Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter a project name (e.g., "calendar-booking-agent")
4. Click "Create"

### 1.2 Enable Google Calendar API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Calendar API"
3. Click on it and press "Enable"

### 1.3 Create a Service Account

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Fill in the details:
   - Service account name: `calendar-agent`
   - Service account ID: (auto-generated)
   - Description: "Service account for calendar booking agent"
4. Click "Create and Continue"
5. Skip the optional permissions (click "Continue")
6. Click "Done"

### 1.4 Generate Service Account Key

1. Find your service account in the credentials list
2. Click on the service account email
3. Go to the "Keys" tab
4. Click "Add Key" → "Create new key"
5. Choose "JSON" format
6. Click "Create" - this downloads the key file
7. **Save this file securely** - you'll need it for configuration

### 1.5 Share Calendar with Service Account

1. Copy the service account email (looks like `calendar-agent@your-project.iam.gserviceaccount.com`)
2. Open Google Calendar
3. Find the calendar you want to use (or create a new one)
4. Click the three dots next to the calendar → "Settings and sharing"
5. Under "Share with specific people", click "Add people"
6. Paste the service account email
7. Set permission to "Make changes to events"
8. Click "Send"

### 1.6 Get Calendar ID

1. In the same calendar settings page
2. Scroll down to "Integrate calendar"
3. Copy the "Calendar ID" (looks like `your-email@gmail.com` or `random-string@group.calendar.google.com`)

## Step 2: Get Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the API key

## Step 3: Local Development Setup

### 3.1 Clone or Download the Project

```bash
git clone <your-repo-url>
cd calendar-booking-agent
```

### 3.2 Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file:
   ```bash
   touch .env
   ```

5. Add the following to `.env`:
   ```env
   GOOGLE_CALENDAR_CREDENTIALS_PATH=/path/to/your/service-account-key.json
   GOOGLE_CALENDAR_ID=your-calendar-id@gmail.com
   GOOGLE_API_KEY=your-gemini-api-key
   PORT=8000
   ```

6. Test the backend:
   ```bash
   python app.py
   ```
   
   Visit `http://localhost:8000/docs` to see the API documentation.

### 3.3 Frontend Setup

1. Open a new terminal and navigate to frontend:
   ```bash
   cd frontend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file (optional):
   ```bash
   echo "BACKEND_URL=http://localhost:8000" > .env
   ```

5. Run the frontend:
   ```bash
   streamlit run app.py
   ```

## Step 4: Testing the Application

1. Ensure both backend and frontend are running
2. Open the Streamlit app (usually at `http://localhost:8501`)
3. Try these test scenarios:

   **Basic Booking:**
   - "Book a meeting tomorrow at 2pm"
   - "Schedule a dentist appointment next Monday at 3:30pm for 45 minutes"

   **Availability Check:**
   - "Am I free tomorrow afternoon?"
   - "Check my availability on Friday"

   **Listing Appointments:**
   - "Show my upcoming appointments"
   - "What's on my calendar this week?"

## Step 5: Deployment

### 5.1 Backend Deployment (Railway)

1. Create account on [Railway](https://railway.app/)
2. Create new project
3. Deploy from GitHub or use Railway CLI:
   ```bash
   railway login
   railway init
   railway up
   ```
4. Add environment variables in Railway dashboard
5. Note the deployment URL

### 5.2 Backend Deployment (Render)

1. Create account on [Render](https://render.com/)
2. New → Web Service → Connect GitHub repo
3. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
4. Add environment variables
5. Deploy

### 5.3 Frontend Deployment (Streamlit Cloud)

1. Push code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy from GitHub repository
4. Set secrets (environment variables):
   ```toml
   BACKEND_URL = "https://your-backend-url.com"
   ```

## Troubleshooting

### Common Issues

1. **"Service account file not found"**
   - Ensure the path in `GOOGLE_CALENDAR_CREDENTIALS_PATH` is absolute
   - Check file permissions

2. **"Calendar ID is not set"**
   - Verify the calendar ID format
   - Ensure the calendar is shared with the service account

3. **"Cannot connect to backend"**
   - Check if backend is running
   - Verify `BACKEND_URL` in frontend
   - Check CORS settings

4. **"No appointments showing"**
   - Verify calendar has events
   - Check timezone settings
   - Ensure service account has read permissions

### Debug Mode

Add to backend `.env` for detailed logs:
```env
DEBUG=true
```

## Security Best Practices

1. **Never commit credentials**:
   - Add `*.json` and `.env` to `.gitignore`
   - Use environment variables for all secrets

2. **Restrict service account permissions**:
   - Only grant calendar access
   - Use least privilege principle

3. **API Key security**:
   - Restrict API key usage in Google Cloud Console
   - Set up quotas and alerts

4. **Production considerations**:
   - Use HTTPS for all communications
   - Implement rate limiting
   - Add authentication if needed

## Next Steps

- Add user authentication
- Support multiple calendars
- Implement recurring appointments
- Add email notifications
- Create appointment templates