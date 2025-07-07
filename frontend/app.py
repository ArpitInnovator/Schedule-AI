# app.py
import streamlit as st
import requests
import json
from datetime import datetime

# Backend URL
BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Schedule AI", layout="centered")

# Helper functions for API calls
def fetch_available_slots():
    """Fetch available time slots from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/available-slots")
        if response.status_code == 200:
            return response.json().get("slots", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch available slots: {e}")
    return []

def send_chat_message(message):
    """Send chat message to backend agent"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": message}
        )
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to send message: {e}")
    return {"response": "Sorry, I'm having trouble connecting to the scheduling service.", "action": "error"}

def book_appointment(slot_id, title, description=""):
    """Book an appointment via backend API"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/book-appointment",
            json={
                "slot_id": slot_id,
                "title": title,
                "description": description
            }
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "message": f"Booking failed: {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Network error: {e}"}

# --- Initialize session state ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there! I'm your AI scheduling assistant. I can help you book appointments, check availability, and manage your schedule. How can I help you today?"}
    ]
if "available_slots" not in st.session_state:
    st.session_state.available_slots = fetch_available_slots()
if "appointment" not in st.session_state:
    st.session_state.appointment = None
if "booking_slot" not in st.session_state:
    st.session_state.booking_slot = None

# --- Header ---
st.markdown("## 🗓 Schedule AI")
st.markdown("I can help you schedule meetings in your calendar. Just tell me what you need.")

# --- Chat history ---
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])
    else:
        st.chat_message("user").write(msg["content"])

# --- Available time slots display ---
if st.session_state.available_slots:
    st.markdown("### 📅 Available Time Slots")
    cols = st.columns(min(len(st.session_state.available_slots), 3))
    for i, slot in enumerate(st.session_state.available_slots[:6]):  # Show max 6 slots
        col_idx = i % 3
        if cols[col_idx].button(slot["display"], key=f"slot_{slot['id']}"):
            # User selected a time slot
            st.session_state.booking_slot = slot
            st.session_state.messages.append({"role": "user", "content": f"I'd like to book {slot['display']}"})
            st.rerun()

# --- Booking form if slot selected ---
if st.session_state.booking_slot and not st.session_state.appointment:
    st.markdown("---")
    st.markdown("### 📝 Book Your Appointment")
    
    with st.form("booking_form"):
        meeting_title = st.text_input("Meeting Title", placeholder="e.g., Team standup, Client call")
        meeting_description = st.text_area("Description (optional)", placeholder="Add any details about the meeting")
        
        submitted = st.form_submit_button("Confirm Booking")
        
        if submitted:
            if meeting_title.strip():
                # Book the appointment
                result = book_appointment(
                    st.session_state.booking_slot["id"],
                    meeting_title,
                    meeting_description
                )
                
                if result.get("success"):
                    st.session_state.appointment = result["appointment"]
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": f"✅ {result['message']}"
                    })
                    # Refresh available slots
                    st.session_state.available_slots = fetch_available_slots()
                    st.session_state.booking_slot = None
                    st.rerun()
                else:
                    st.error(result.get("message", "Booking failed"))
            else:
                st.error("Please enter a meeting title")

# --- Text input for free chat ---
user_input = st.chat_input("Type a message")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Send message to backend agent
    agent_response = send_chat_message(user_input)
    
    # Handle agent response
    response_text = agent_response.get("response", "I'm sorry, I didn't understand that.")
    action = agent_response.get("action", "")
    
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    
    # Update available slots if agent suggests showing them
    if action == "show_slots" and "slots" in agent_response:
        st.session_state.available_slots = agent_response["slots"]
    elif action == "show_slots":
        # Refresh from backend
        st.session_state.available_slots = fetch_available_slots()
    
    st.rerun()

# --- Appointment confirmation display ---
if st.session_state.appointment:
    st.markdown("---")
    st.markdown("### ✅ Appointment Confirmed")
    
    appointment = st.session_state.appointment
    datetime_obj = datetime.fromisoformat(appointment["datetime"].replace('Z', '+00:00'))
    formatted_date = datetime_obj.strftime("%A, %B %d, %Y at %I:%M %p")
    
    st.success(f"""
    **{appointment['title']}**  
    📅 {formatted_date}  
    📝 {appointment.get('description', 'No description')}  
    🆔 Appointment ID: `{appointment['id']}`
    """)
    
    if st.button("Book Another Appointment"):
        st.session_state.appointment = None
        st.session_state.available_slots = fetch_available_slots()
        st.rerun()

# --- Refresh slots button ---
if st.button("🔄 Refresh Available Times"):
    st.session_state.available_slots = fetch_available_slots()
    st.rerun()

