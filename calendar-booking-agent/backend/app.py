"""FastAPI backend for the calendar booking agent."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import uvicorn

from agent import get_booking_agent
from config import settings, validate_settings


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Calendar Booking Agent API",
    description="API for conversational calendar appointment booking",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    session_id: str
    success: bool = True
    error: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup."""
    try:
        validate_settings()
        logger.info("Configuration validated successfully")
        # Initialize the agent to catch any initialization errors early
        get_booking_agent()
        logger.info("Booking agent initialized successfully")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Calendar Booking Agent API",
        "endpoints": {
            "/chat": "POST - Send messages to the booking agent",
            "/health": "GET - Health check",
            "/docs": "GET - API documentation"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Try to get the agent to ensure it's working
        agent = get_booking_agent()
        return {
            "status": "healthy",
            "service": "calendar-booking-agent",
            "agent_status": "initialized" if agent else "not initialized"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the booking agent.
    
    Args:
        request: Chat request with message and optional session ID
        
    Returns:
        Agent response with session ID
    """
    try:
        # Get the booking agent
        agent = get_booking_agent()
        
        # Generate session ID if not provided
        session_id = request.session_id or f"session_{hash(request.message)}"
        
        # Process the message
        logger.info(f"Processing message: {request.message[:50]}...")
        
        try:
            # Invoke the agent
            result = agent.invoke({
                "input": request.message
            })
            
            # Extract the output
            response = result.get("output", "I'm sorry, I couldn't process your request.")
            
        except Exception as agent_error:
            logger.error(f"Agent error: {agent_error}")
            response = (
                "I apologize, but I encountered an error while processing your request. "
                "Please try again or rephrase your message."
            )
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return ChatResponse(
            response="I'm sorry, but I'm unable to process your request at the moment.",
            session_id=request.session_id or "error",
            success=False,
            error=str(e)
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Global error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "An unexpected error occurred",
            "detail": str(exc) if settings.debug else None
        }
    )


# Add debug mode based on environment
if hasattr(settings, 'debug'):
    app.debug = settings.debug


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info"
    )