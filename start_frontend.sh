#!/bin/bash

# Start the Streamlit frontend
echo "Starting ScheduleAI Frontend..."
echo "Frontend will be available at: http://localhost:8501"
echo ""
echo "Make sure the backend is running on port 8000"
echo "Press Ctrl+C to stop the server"
echo ""

cd frontend
streamlit run app.py --server.port 8501