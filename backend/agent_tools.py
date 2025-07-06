from datetime import datetime, timedelta
from typing import List, Dict, Optional
from langchain.tools import tool
from pydantic import BaseModel, Field
import json
from .calendar_client import CalendarClient


# Initialize the calendar client
calendar_client = CalendarClient()


class AvailabilityQuery(BaseModel):
    """Input for checking availability."""
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format") 
    duration_minutes: int = Field(60, description="Duration of the meeting in minutes")
    
    
class EventCreation(BaseModel):
    """Input for creating a calendar event."""
    title: str = Field(..., description="Title of the meeting")
    start_datetime: str = Field(..., description="Start date and time in ISO format")
    end_datetime: str = Field(..., description="End date and time in ISO format")
    description: str = Field("", description="Description of the meeting")
    attendees: Optional[List[str]] = Field(None, description="List of attendee email addresses")


@tool("check_availability", args_schema=AvailabilityQuery)
def check_availability(start_date: str, end_date: str, duration_minutes: int = 60) -> str:
    """
    Check calendar availability and return available time slots.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format  
        duration_minutes: Duration of the meeting in minutes (default 60)
        
    Returns:
        JSON string with available time slots
    """
    try:
        # Parse dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59)
        
        # Get available slots
        available_slots = calendar_client.find_available_slots(
            start_dt, end_dt, duration_minutes
        )
        
        # Format the response
        if not available_slots:
            return json.dumps({
                "status": "no_availability",
                "message": f"No available slots found between {start_date} and {end_date} for {duration_minutes} minutes",
                "slots": []
            })
        
        # Format slots for better readability
        formatted_slots = []
        for slot in available_slots:
            start_time = datetime.fromisoformat(slot['start'])
            end_time = datetime.fromisoformat(slot['end'])
            formatted_slots.append({
                "start": slot['start'],
                "end": slot['end'],
                "start_formatted": start_time.strftime("%A, %B %d at %I:%M %p"),
                "end_formatted": end_time.strftime("%I:%M %p"),
                "duration_minutes": slot['duration_minutes']
            })
        
        return json.dumps({
            "status": "success", 
            "message": f"Found {len(formatted_slots)} available slots",
            "slots": formatted_slots
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error checking availability: {str(e)}",
            "slots": []
        })


@tool("create_calendar_event", args_schema=EventCreation)
def create_calendar_event(title: str, start_datetime: str, end_datetime: str, 
                         description: str = "", attendees: Optional[List[str]] = None) -> str:
    """
    Create a new calendar event.
    
    Args:
        title: Title of the meeting
        start_datetime: Start date and time in ISO format (e.g., "2024-01-15T14:00:00")
        end_datetime: End date and time in ISO format (e.g., "2024-01-15T15:00:00") 
        description: Description of the meeting
        attendees: List of attendee email addresses
        
    Returns:
        JSON string with creation result
    """
    try:
        # Parse datetime strings
        start_dt = datetime.fromisoformat(start_datetime)
        end_dt = datetime.fromisoformat(end_datetime)
        
        # Create the event
        event = calendar_client.create_event(
            title=title,
            start_time=start_dt,
            end_time=end_dt,
            description=description,
            attendees=attendees
        )
        
        if event:
            return json.dumps({
                "status": "success",
                "message": f"Successfully created event '{title}'",
                "event": {
                    "id": event.get('id'),
                    "title": title,
                    "start": start_datetime,
                    "end": end_datetime,
                    "link": event.get('htmlLink', ''),
                    "description": description
                }
            })
        else:
            return json.dumps({
                "status": "error", 
                "message": "Failed to create calendar event",
                "event": None
            })
            
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error creating event: {str(e)}",
            "event": None
        })


@tool("get_busy_times")
def get_busy_times(start_date: str, end_date: str) -> str:
    """
    Get busy time slots to understand calendar conflicts.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        JSON string with busy time slots
    """
    try:
        # Parse dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59)
        
        # Get busy times
        busy_times = calendar_client.get_busy_times(start_dt, end_dt)
        
        # Format the response
        formatted_busy = []
        for busy in busy_times:
            start_time = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
            formatted_busy.append({
                "start": busy['start'],
                "end": busy['end'],
                "start_formatted": start_time.strftime("%A, %B %d at %I:%M %p"),
                "end_formatted": end_time.strftime("%I:%M %p"),
                "summary": busy.get('summary', 'Busy')
            })
        
        return json.dumps({
            "status": "success",
            "busy_times": formatted_busy,
            "count": len(formatted_busy)
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error getting busy times: {str(e)}",
            "busy_times": []
        })


# Export all tools for the agent
calendar_tools = [check_availability, create_calendar_event, get_busy_times]