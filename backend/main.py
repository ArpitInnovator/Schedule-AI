from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Calendar Booking Agent API",
    description="API for conversational calendar booking using Google Calendar",
    version="1.0.0"
)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ChatMessage(BaseModel):
    message: str
    chat_history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    response: str
    actions_taken: Optional[List[str]] = []
    status: str = "success"

# Temporary simple chat responses (without LangChain for now)
def get_simple_response(message: str) -> str:
    """Simple rule-based responses for testing"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["hello", "hi", "hey"]):
        return "Hello! I'm your calendar booking assistant. I can help you schedule appointments. What would you like to book?"
    
    elif any(word in message_lower for word in ["book", "schedule", "appointment", "meeting"]):
        return "I'd be happy to help you book an appointment! Please tell me:\n- What date would you like?\n- What time works best?\n- How long should the meeting be?\n- What's the purpose of the meeting?"
    
    elif any(word in message_lower for word in ["available", "free", "open"]):
        return "Let me check your calendar availability. Could you specify a date range you're interested in?"
    
    elif any(word in message_lower for word in ["cancel", "reschedule", "change"]):
        return "I can help you modify existing appointments. Could you tell me which appointment you'd like to change?"
    
    else:
        return "I'm here to help you with calendar bookings! You can ask me to:\n- Book a new appointment\n- Check availability\n- Reschedule existing meetings\n\nWhat would you like to do?"

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Calendar Booking Agent API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Calendar Booking Agent API is running",
        "version": "1.0.0"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """
    Main chat endpoint for conversational booking
    """
    try:
        # For now, use simple responses
        response = get_simple_response(chat_message.message)
        
        return ChatResponse(
            response=response,
            actions_taken=[],
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/greeting")
async def get_greeting():
    """Get a greeting message from the agent"""
    return {
        "message": "Hello! I'm your AI calendar booking assistant. I can help you schedule appointments, check availability, and manage your calendar. How can I assist you today?"
    }

@app.get("/test-calendar")
async def test_calendar():
    """Test calendar connection (simplified)"""
    try:
        # Try to import and test calendar client
        from calendar_client import CalendarClient
        
        calendar_client = CalendarClient()
        
        # Basic test - this will fail gracefully if credentials aren't set up
        return {
            "status": "Calendar client initialized",
            "message": "Calendar integration is ready (credentials needed for full functionality)"
        }
        
    except Exception as e:
        return {
            "status": "Calendar client not available",
            "message": f"Calendar setup needed: {str(e)}",
            "setup_required": True
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)