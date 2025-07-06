#!/bin/bash

# Start the FastAPI backend
echo "Starting ScheduleAI Backend..."
echo "Backend will be available at: http://localhost:8000"
echo "API Documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000