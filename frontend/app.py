# app.py
import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BACKEND_URL = "http://localhost:8000"  # Change this for production deployment

st.set_page_config(
    page_title="ScheduleAI - Calendar Booking Assistant", 
    page_icon="📅",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 2rem;
    }
    .system-status {
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    .status-healthy {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .status-error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)


def check_backend_health() -> Dict:
    """Check if the backend is available and healthy."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Add agent_available field for compatibility
            data["agent_available"] = data.get("status") == "healthy"
            return data
        else:
            return {"status": "error", "agent_available": False}
    except requests.exceptions.RequestException:
        return {"status": "error", "agent_available": False}


def send_message_to_backend(message: str, chat_history: List[Dict]) -> Dict:
    """Send a message to the backend and get the response."""
    try:
        payload = {
            "message": message,
            "chat_history": chat_history
        }
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "status": "error",
                "response": f"Backend error: {response.status_code}",
                "error": "HTTP error"
            }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "response": f"Connection error: Could not reach the booking agent. Please check if the backend is running.",
            "error": str(e)
        }


def get_greeting_from_backend() -> str:
    """Get the greeting message from the backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/greeting", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("message", "Hello! I'm your calendar booking assistant.")
        else:
            return "Hello! I'm your calendar booking assistant."
    except requests.exceptions.RequestException:
        return "Hello! I'm your calendar booking assistant. (Note: Backend connection unavailable)"


# Initialize session state
if "messages" not in st.session_state:
    # Check backend and get greeting
    health = check_backend_health()
    greeting = get_greeting_from_backend()
    
    st.session_state.messages = [
        {"role": "assistant", "content": greeting}
    ]
    st.session_state.backend_status = health

if "backend_status" not in st.session_state:
    st.session_state.backend_status = check_backend_health()

# Header
st.markdown("# 📅 ScheduleAI")
st.markdown("*Your intelligent calendar booking assistant*")

# Backend status indicator
status = st.session_state.backend_status
if status.get("status") == "healthy" and status.get("agent_available", False):
    st.markdown(
        '<div class="system-status status-healthy">✅ System operational - AI agent ready</div>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        '<div class="system-status status-error">⚠️ Limited functionality - Backend unavailable</div>',
        unsafe_allow_html=True
    )

# Environment check (if available)
if "environment_check" in status:
    env_check = status["environment_check"]
    missing_configs = [key for key, value in env_check.items() if not value]
    if missing_configs:
        st.warning(f"⚙️ Configuration needed: {', '.join(missing_configs)}")

# Chat container
chat_container = st.container()

with chat_container:
    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            st.chat_message("assistant", avatar="🤖").write(message["content"])
        else:
            st.chat_message("user", avatar="👤").write(message["content"])

# Chat input
if prompt := st.chat_input("Tell me what you'd like to schedule..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    st.chat_message("user", avatar="👤").write(prompt)
    
    # Prepare chat history for backend (exclude the current message)
    chat_history = st.session_state.messages[:-1]
    
    # Send to backend and get response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            result = send_message_to_backend(prompt, chat_history)
        
        if result.get("status") == "success":
            response = result["response"]
            st.write(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Show actions taken if available
            if result.get("actions_taken"):
                with st.expander("Actions Taken"):
                    for action in result["actions_taken"]:
                        st.write(f"✅ {action}")
                
        else:
            error_response = result.get("response", "I'm having trouble processing your request.")
            st.error(error_response)
            st.session_state.messages.append({"role": "assistant", "content": error_response})

# Sidebar with additional information
with st.sidebar:
    st.markdown("### 🛠️ System Information")
    
    # Refresh backend status
    if st.button("🔄 Refresh Status"):
        st.session_state.backend_status = check_backend_health()
        st.rerun()
    
    # Display detailed status
    status = st.session_state.backend_status
    st.markdown(f"**Status:** {status.get('status', 'unknown')}")
    st.markdown(f"**Agent Available:** {'✅' if status.get('agent_available', False) else '❌'}")
    
    if "environment_check" in status:
        st.markdown("**Configuration:**")
        env_check = status["environment_check"]
        for key, value in env_check.items():
            icon = "✅" if value else "❌"
            st.markdown(f"- {key}: {icon}")
    
    st.markdown("---")
    st.markdown("### 📋 Quick Actions")
    
    # Quick action buttons
    quick_actions = [
        "Schedule a meeting tomorrow at 2 PM",
        "Check my availability this week",
        "Book a 30-minute call on Friday",
        "Find time for a team meeting next week"
    ]
    
    for action in quick_actions:
        if st.button(action, key=f"quick_{action}"):
            # Simulate user input
            st.session_state.messages.append({"role": "user", "content": action})
            
            # Get response from backend
            chat_history = st.session_state.messages[:-1]
            result = send_message_to_backend(action, chat_history)
            
            if result.get("status") == "success":
                response = result["response"]
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                error_response = result.get("response", "I'm having trouble processing your request.")
                st.session_state.messages.append({"role": "assistant", "content": error_response})
            
            st.rerun()
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    This is an AI-powered calendar booking assistant that can:
    - Check your calendar availability
    - Schedule meetings and appointments
    - Suggest alternative time slots
    - Create calendar events with confirmation
    
    Powered by LangChain, Gemini AI, and Google Calendar API.
    """)
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        greeting = get_greeting_from_backend()
        st.session_state.messages = [
            {"role": "assistant", "content": greeting}
        ]
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "*💡 Tip: Try natural language like 'Schedule a meeting with John tomorrow at 3 PM' or 'What's my availability next week?'*"
)

