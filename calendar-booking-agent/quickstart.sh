#!/bin/bash
# Quick start script for Calendar Booking Agent

echo "🚀 Calendar Booking Agent - Quick Start"
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check if backend .env exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  No backend/.env file found!"
    echo "Creating from template..."
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo "✅ Created backend/.env - Please edit it with your configuration!"
        echo "   Required: GOOGLE_CALENDAR_CREDENTIALS_PATH, GOOGLE_CALENDAR_ID, GOOGLE_API_KEY"
        exit 1
    fi
fi

# Install backend dependencies if needed
echo ""
echo "📦 Checking backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing backend dependencies..."
    pip install -r requirements.txt
fi

# Start backend
echo ""
echo "🚀 Starting backend server..."
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use. Backend might already be running."
else
    python app.py &
    BACKEND_PID=$!
    echo "✅ Backend started (PID: $BACKEND_PID)"
    sleep 3
fi

# Install frontend dependencies if needed
echo ""
echo "📦 Checking frontend dependencies..."
cd ../frontend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

if ! python -c "import streamlit" 2>/dev/null; then
    echo "Installing frontend dependencies..."
    pip install -r requirements.txt
fi

# Start frontend
echo ""
echo "🚀 Starting frontend..."
if check_port 8501; then
    echo "⚠️  Port 8501 is already in use. Frontend might already be running."
    echo ""
    echo "✅ Open http://localhost:8501 in your browser"
else
    streamlit run app.py &
    FRONTEND_PID=$!
    echo "✅ Frontend started (PID: $FRONTEND_PID)"
    echo ""
    echo "✅ Application is ready!"
    echo "   Open http://localhost:8501 in your browser"
fi

echo ""
echo "Press Ctrl+C to stop both services..."

# Wait and handle shutdown
trap 'echo ""; echo "Shutting down..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT

wait