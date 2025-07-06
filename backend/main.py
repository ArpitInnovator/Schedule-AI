from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import the booking agent
try:
    from .booking_agent import booking_agent
    agent_available = True
except Exception as e:
    print(f"Warning: Could not load booking agent: {e}")
    agent_available = False

app = FastAPI(
    title="Calendar Booking Agent API",
    description="API for conversational calendar booking using LangChain and Google Calendar",
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
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    chat_history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    success: bool
    response: str
    error: Optional[str] = None
    intermediate_steps: Optional[List[Any]] = None


class HealthResponse(BaseModel):
    status: str
    agent_available: bool
    environment_check: Dict[str, bool]


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Calendar Booking Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify system status."""
    
    # Check environment variables
    env_check = {
        "google_api_key": bool(os.getenv('GOOGLE_API_KEY')),
        "google_service_account": bool(os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')),
        "google_calendar_id": bool(os.getenv('GOOGLE_CALENDAR_ID'))
    }
    
    return HealthResponse(
        status="healthy" if agent_available else "degraded",
        agent_available=agent_available,
        environment_check=env_check
    )


@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Main chat endpoint for interacting with the booking agent.
    
    Args:
        request: Chat request with message and optional history
        
    Returns:
        Chat response with agent's reply
    """
    if not agent_available:
        return ChatResponse(
            success=False,
            response="I'm sorry, but the booking agent is currently unavailable. Please check the system configuration.",
            error="Agent not available"
        )
    
    try:
        # Convert Pydantic models to dictionaries for the agent
        chat_history = []
        if request.chat_history:
            chat_history = [
                {"role": msg.role, "content": msg.content}
                for msg in request.chat_history
            ]
        
        # Process the message with the agent
        result = booking_agent.process_message(
            message=request.message,
            chat_history=chat_history
        )
        
        return ChatResponse(
            success=result["success"],
            response=result["response"],
            error=result.get("error"),
            intermediate_steps=result.get("intermediate_steps")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )


@app.get("/greeting", response_model=Dict[str, str])
async def get_greeting():
    """Get a greeting message for new conversations."""
    if not agent_available:
        return {
            "greeting": "Welcome to the Calendar Booking Assistant! Currently running in limited mode."
        }
    
    try:
        greeting = booking_agent.get_greeting()
        return {"greeting": greeting}
    except Exception as e:
        return {
            "greeting": "Hi there! I'm your calendar booking assistant. How can I help you schedule something today?"
        }


@app.post("/test-calendar")
async def test_calendar_connection():
    """Test endpoint to verify calendar connection."""
    if not agent_available:
        return {
            "success": False,
            "message": "Agent not available"
        }
    
    try:
        from datetime import datetime, timedelta
        from .calendar_client import CalendarClient
        
        client = CalendarClient()
        
        # Test basic calendar operations
        start_date = datetime.now()
        end_date = start_date + timedelta(days=1)
        
        busy_times = client.get_busy_times(start_date, end_date)
        available_slots = client.find_available_slots(start_date, end_date)
        
        return {
            "success": True,
            "message": "Calendar connection test successful",
            "busy_times_count": len(busy_times),
            "available_slots_count": len(available_slots)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Calendar connection test failed: {str(e)}"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)