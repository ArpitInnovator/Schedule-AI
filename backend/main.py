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

# Try to import the booking agent
agent_available = False
booking_agent = None

try:
    from booking_agent import booking_agent
    if booking_agent is not None:
        agent_available = True
        print("✅ Booking agent loaded successfully")
    else:
        agent_available = False
        print("❌ Booking agent failed to initialize (see earlier error)")
except Exception as e:
    agent_available = False
    print(f"⚠️  Warning: Could not load booking agent: {e}")
    print("API will run with limited functionality")

# Pydantic models for request/response
class ChatMessage(BaseModel):
    message: str
    chat_history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    response: str
    actions_taken: Optional[List[str]] = []
    status: str = "success"

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
        "agent_available": agent_available,
        "version": "1.0.0"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """
    Main chat endpoint for conversational booking
    """
    try:
        if not agent_available or not booking_agent:
            # Fallback response when agent is not available
            return ChatResponse(
                response="I'm sorry, but the calendar booking agent is currently unavailable. Please check that the Google API credentials are properly configured.",
                actions_taken=["error_fallback"],
                status="error"
            )
        
        # Process the message with the real booking agent
        result = booking_agent.process_message(
            message=chat_message.message,
            chat_history=chat_message.chat_history
        )
        
        if result.get("success", False):
            # Extract any tool actions from intermediate steps
            actions_taken = []
            for step in result.get("intermediate_steps", []):
                if hasattr(step[0], 'tool'):
                    actions_taken.append(step[0].tool)
            
            return ChatResponse(
                response=result["response"],
                actions_taken=actions_taken,
                status="success"
            )
        else:
            return ChatResponse(
                response=result.get("response", "I encountered an error processing your request."),
                actions_taken=[],
                status="error"
            )
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/greeting")
async def get_greeting():
    """Get a greeting message from the agent"""
    try:
        if agent_available and booking_agent:
            greeting = booking_agent.get_greeting()
        else:
            greeting = "Hello! I'm your calendar booking assistant. Please note that some features may be limited due to configuration issues."
        
        return {
            "message": greeting,
            "agent_available": agent_available
        }
    except Exception as e:
        return {
            "message": "Hello! I'm your calendar booking assistant. How can I help you schedule an appointment today?",
            "agent_available": False,
            "error": str(e)
        }

@app.get("/test-calendar")
async def test_calendar():
    """Test calendar connection and agent functionality"""
    try:
        # Test calendar client import
        from calendar_client import CalendarClient
        
        calendar_client = CalendarClient()
        
        # Test basic functionality
        test_results = {
            "calendar_client": "✅ Calendar client initialized",
            "agent_available": agent_available,
            "environment_check": {}
        }
        
        # Check environment variables
        required_vars = ["GOOGLE_API_KEY"]
        optional_vars = ["GOOGLE_SERVICE_ACCOUNT_JSON", "GOOGLE_CALENDAR_ID"]
        
        for var in required_vars:
            test_results["environment_check"][var] = "✅ Set" if os.getenv(var) else "❌ Missing"
        
        for var in optional_vars:
            test_results["environment_check"][var] = "✅ Set" if os.getenv(var) else "⚠️  Not set (using defaults)"
        
        # Test a simple availability check if possible
        if agent_available:
            test_results["agent_test"] = "✅ Agent ready"
        else:
            test_results["agent_test"] = "❌ Agent not available"
        
        return {
            "status": "test_complete",
            "results": test_results,
            "message": "Calendar booking system test completed. Check results for any missing configuration."
        }
        
    except Exception as e:
        return {
            "status": "test_failed",
            "message": f"Calendar test failed: {str(e)}",
            "suggestion": "Please check your environment variables and credentials"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)