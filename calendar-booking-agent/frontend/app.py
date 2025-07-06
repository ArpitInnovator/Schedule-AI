"""Streamlit chat interface for the calendar booking agent."""

import streamlit as st
import requests
import os
from datetime import datetime
import json
from typing import Dict, Optional

# Page configuration
st.set_page_config(
    page_title="Calendar Booking Assistant",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better chat appearance
st.markdown("""
<style>
    /* Main container styling */
    .main {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Chat message styling */
    .user-message {
        background-color: #007AFF;
        color: white;
        padding: 10px 15px;
        border-radius: 18px;
        margin: 5px 0;
        max-width: 70%;
        float: right;
        clear: both;
        word-wrap: break-word;
    }
    
    .assistant-message {
        background-color: #E9E9EB;
        color: #000;
        padding: 10px 15px;
        border-radius: 18px;
        margin: 5px 0;
        max-width: 70%;
        float: left;
        clear: both;
        word-wrap: break-word;
    }
    
    .chat-container {
        height: 500px;
        overflow-y: auto;
        padding: 20px;
        border: 1px solid #ddd;
        border-radius: 10px;
        background-color: #f5f5f5;
        margin-bottom: 20px;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 20px;
        border: 2px solid #007AFF;
        padding: 10px 20px;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 20px;
        background-color: #007AFF;
        color: white;
        border: none;
        padding: 10px 30px;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        background-color: #0051D5;
    }
    
    /* Header styling */
    h1 {
        color: #007AFF;
        text-align: center;
        margin-bottom: 30px;
    }
    
    /* Clear float */
    .clear {
        clear: both;
    }
</style>
""", unsafe_allow_html=True)

# Backend configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add welcome message
    st.session_state.messages.append({
        "role": "assistant",
        "content": "👋 Hello! I'm your Calendar Booking Assistant. I can help you:\n\n"
                  "• 📅 Book appointments\n"
                  "• 🔍 Check calendar availability\n"
                  "• 📋 List upcoming appointments\n\n"
                  "How can I help you today?"
    })

if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{datetime.now().timestamp()}"


def send_message_to_backend(message: str, session_id: str) -> Optional[Dict]:
    """Send message to the backend API."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={
                "message": message,
                "session_id": session_id
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to the backend: {str(e)}")
        return None


def display_chat_history():
    """Display the chat history with custom styling."""
    chat_html = '<div class="chat-container">'
    
    for message in st.session_state.messages:
        if message["role"] == "user":
            chat_html += f'<div class="user-message">{message["content"]}</div>'
        else:
            # Convert markdown-style formatting to HTML for assistant messages
            content = message["content"]
            content = content.replace("**", "<strong>").replace("**", "</strong>")
            content = content.replace("\n", "<br>")
            chat_html += f'<div class="assistant-message">{content}</div>'
        chat_html += '<div class="clear"></div>'
    
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)


# Main app layout
st.title("📅 Calendar Booking Assistant")

# Create two columns for better layout
col1, col2 = st.columns([2, 1])

with col1:
    # Display chat history
    display_chat_history()
    
    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Type your message here...",
            placeholder="e.g., 'Book a meeting tomorrow at 2pm'",
            label_visibility="collapsed"
        )
        submit_button = st.form_submit_button("Send", use_container_width=True)
    
    if submit_button and user_input:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Send to backend
        with st.spinner("Thinking..."):
            response = send_message_to_backend(user_input, st.session_state.session_id)
        
        if response and response.get("success"):
            # Add assistant response to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": response.get("response", "I couldn't process your request.")
            })
            # Update session ID if provided
            if response.get("session_id"):
                st.session_state.session_id = response["session_id"]
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "I'm sorry, I'm having trouble connecting to my calendar service. Please try again."
            })
        
        # Rerun to update the chat display
        st.rerun()

with col2:
    # Sidebar information
    st.markdown("### 💡 Quick Tips")
    st.markdown(
        """
        **Example requests:**
        - "Book a meeting tomorrow at 2pm"
        - "Schedule a 1-hour call next Monday morning"
        - "Check if I'm free this Friday afternoon"
        - "Show my appointments for next week"
        - "Book a dentist appointment on Dec 15 at 3:30pm"
        
        **Natural language support:**
        - Dates: "tomorrow", "next Monday", "December 15"
        - Times: "2pm", "morning", "afternoon"
        - Durations: "30 minutes", "1 hour"
        """
    )
    
    # Connection status
    st.markdown("### 🔌 Connection Status")
    try:
        health_response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if health_response.status_code == 200:
            st.success("✅ Connected to backend")
        else:
            st.error("❌ Backend unhealthy")
    except:
        st.error("❌ Cannot reach backend")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "👋 Hello! I'm your Calendar Booking Assistant. How can I help you today?"
        }]
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666;'>Calendar Booking Assistant v1.0 | Powered by Gemini & LangChain</p>",
    unsafe_allow_html=True
)