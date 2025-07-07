from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import uuid

app = FastAPI(title="Schedule AI Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with database in production)
appointments = {}
available_slots = []

# Generate sample available time slots for the next 7 days
def generate_available_slots():
    slots = []
    base_date = datetime.now()
    for day in range(1, 8):  # Next 7 days
        date = base_date + timedelta(days=day)
        if date.weekday() < 5:  # Weekdays only
            for hour in [9, 10, 11, 14, 15, 16, 17]:  # Business hours
                slot_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
                slots.append({
                    "id": f"{date.strftime('%Y%m%d')}_{hour:02d}00",
                    "datetime": slot_time.isoformat(),
                    "display": slot_time.strftime("%A, %B %d at %I:%M %p"),
                    "available": True
                })
    return slots

# Initialize available slots
available_slots = generate_available_slots()

# Models
class AppointmentRequest(BaseModel):
    slot_id: str
    title: str
    description: Optional[str] = ""
    attendee_email: Optional[str] = ""

class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict] = {}

class AppointmentResponse(BaseModel):
    id: str
    slot_id: str
    title: str
    description: str
    datetime: str
    status: str

@app.get("/")
def read_root():
    return {"message": "Schedule AI Backend is running"}

@app.get("/available-slots")
def get_available_slots():
    """Get all available time slots"""
    return {"slots": [slot for slot in available_slots if slot["available"]]}

@app.post("/book-appointment")
def book_appointment(request: AppointmentRequest):
    """Book an appointment"""
    # Find the slot
    slot = next((s for s in available_slots if s["id"] == request.slot_id), None)
    if not slot:
        raise HTTPException(status_code=404, detail="Time slot not found")
    
    if not slot["available"]:
        raise HTTPException(status_code=400, detail="Time slot is no longer available")
    
    # Create appointment
    appointment_id = str(uuid.uuid4())
    appointment = {
        "id": appointment_id,
        "slot_id": request.slot_id,
        "title": request.title,
        "description": request.description,
        "datetime": slot["datetime"],
        "attendee_email": request.attendee_email,
        "status": "confirmed",
        "created_at": datetime.now().isoformat()
    }
    
    # Store appointment
    appointments[appointment_id] = appointment
    
    # Mark slot as unavailable
    slot["available"] = False
    
    return {
        "success": True,
        "appointment": appointment,
        "message": f"Appointment '{request.title}' booked successfully for {slot['display']}"
    }

@app.get("/appointments/{appointment_id}")
def get_appointment(appointment_id: str):
    """Get a specific appointment"""
    if appointment_id not in appointments:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointments[appointment_id]

@app.get("/appointments")
def get_all_appointments():
    """Get all appointments"""
    return {"appointments": list(appointments.values())}

@app.post("/chat")
def chat_with_agent(message: ChatMessage):
    """Process chat message with AI agent"""
    user_message = message.message.lower()
    
    # Simple rule-based agent (replace with actual AI/LLM in production)
    if any(keyword in user_message for keyword in ["book", "schedule", "appointment", "meeting"]):
        available_count = len([s for s in available_slots if s["available"]])
        return {
            "response": f"I'd be happy to help you schedule an appointment! I found {available_count} available time slots. Please select one of the available times shown above, or let me know your preferred time and I'll check availability.",
            "action": "show_slots",
            "slots": [slot for slot in available_slots if slot["available"]][:5]  # Show first 5 available
        }
    
    elif any(keyword in user_message for keyword in ["available", "free", "open", "time"]):
        available_slots_response = [slot for slot in available_slots if slot["available"]][:10]
        return {
            "response": f"Here are the available time slots I found:",
            "action": "show_slots", 
            "slots": available_slots_response
        }
    
    elif any(keyword in user_message for keyword in ["cancel", "reschedule", "change"]):
        return {
            "response": "I can help you cancel or reschedule an appointment. Could you please provide your appointment ID or the details of the appointment you'd like to modify?",
            "action": "help_modify"
        }
    
    elif any(keyword in user_message for keyword in ["hello", "hi", "hey", "help"]):
        return {
            "response": "Hello! I'm your scheduling assistant. I can help you:\n• Book new appointments\n• Check available time slots\n• Reschedule existing appointments\n• Answer questions about scheduling\n\nWhat would you like to do?",
            "action": "greeting"
        }
    
    else:
        return {
            "response": "I understand you're looking for scheduling assistance. I can help you book appointments, check availability, or manage existing bookings. What specific scheduling task can I help you with?",
            "action": "clarify"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)