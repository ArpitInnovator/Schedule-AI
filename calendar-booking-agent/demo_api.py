#!/usr/bin/env python3
"""
Demo script showing how to interact with the Calendar Booking Agent API.
"""

import requests
import json
from datetime import datetime, timedelta

# API configuration
API_URL = "http://localhost:8000"  # Change this to your deployed URL

def demo_chat(message: str, session_id: str = None):
    """Send a message to the chat API and print the response."""
    print(f"\n👤 User: {message}")
    
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "message": message,
                "session_id": session_id or f"demo_{datetime.now().timestamp()}"
            }
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"🤖 Assistant: {data['response']}")
        
        return data.get('session_id', session_id)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return session_id


def main():
    """Run demo conversations."""
    print("=" * 60)
    print("🚀 Calendar Booking Agent API Demo")
    print("=" * 60)
    
    # Check if API is running
    try:
        health = requests.get(f"{API_URL}/health")
        if health.status_code == 200:
            print("✅ API is healthy and running")
        else:
            print("⚠️  API returned unhealthy status")
    except:
        print("❌ Cannot connect to API. Make sure the backend is running.")
        print(f"   Expected API URL: {API_URL}")
        return
    
    # Demo conversation 1: Simple booking
    print("\n" + "-" * 60)
    print("Demo 1: Simple Booking")
    print("-" * 60)
    
    session_id = demo_chat("Hello!")
    session_id = demo_chat("I need to book a meeting tomorrow at 2pm", session_id)
    session_id = demo_chat("It's a team standup meeting for 30 minutes", session_id)
    
    # Demo conversation 2: Check availability
    print("\n" + "-" * 60)
    print("Demo 2: Check Availability")
    print("-" * 60)
    
    session_id = demo_chat("Am I free this Friday afternoon?")
    session_id = demo_chat("What about next Monday morning?", session_id)
    
    # Demo conversation 3: List appointments
    print("\n" + "-" * 60)
    print("Demo 3: List Appointments")
    print("-" * 60)
    
    session_id = demo_chat("Show me my upcoming appointments")
    
    # Demo conversation 4: Complex booking
    print("\n" + "-" * 60)
    print("Demo 4: Complex Booking Request")
    print("-" * 60)
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%B %d")
    session_id = demo_chat(
        f"Schedule a dentist appointment on {tomorrow} at 3:30pm for 45 minutes. "
        "Add a note to arrive 10 minutes early for paperwork."
    )
    
    print("\n" + "=" * 60)
    print("Demo completed! 🎉")
    print("=" * 60)


if __name__ == "__main__":
    main()