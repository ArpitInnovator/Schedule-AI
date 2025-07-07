import pytz
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from langchain.tools import tool
from pydantic import BaseModel, Field
import json
from calendar_client import CalendarClient


# Initialize the calendar client and UTC+5:30 timezone
calendar_client = CalendarClient()
UTC_5_30_TIMEZONE = pytz.timezone('Asia/Kolkata')  # UTC+5:30


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
    Check calendar availability and return available time slots in UTC+5:30 timezone.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format  
        duration_minutes: Duration of the meeting in minutes (default 60)
        
    Returns:
        JSON string with available time slots in UTC+5:30
    """
    try:
        # Parse dates and set to start/end of day in UTC+5:30 timezone
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        start_dt = UTC_5_30_TIMEZONE.localize(start_dt.replace(hour=0, minute=0, second=0))
        
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        end_dt = UTC_5_30_TIMEZONE.localize(end_dt.replace(hour=23, minute=59, second=59))
        
        # Get available slots
        available_slots = calendar_client.find_available_slots(
            start_dt, end_dt, duration_minutes
        )
        
        # Format the response
        if not available_slots:
            return json.dumps({
                "status": "no_availability",
                "message": f"No available slots found between {start_date} and {end_date} for {duration_minutes} minutes (UTC+5:30)",
                "slots": []
            })
        
        # Format slots for better readability in UTC+5:30
        formatted_slots = []
        for slot in available_slots:
            start_time = calendar_client._parse_datetime_with_timezone(slot['start'])
            end_time = calendar_client._parse_datetime_with_timezone(slot['end'])
            formatted_slots.append({
                "start": slot['start'],
                "end": slot['end'],
                "start_formatted": start_time.strftime("%A, %B %d at %I:%M %p UTC+5:30"),
                "end_formatted": end_time.strftime("%I:%M %p UTC+5:30"),
                "duration_minutes": slot['duration_minutes']
            })
        
        return json.dumps({
            "status": "success", 
            "message": f"Found {len(formatted_slots)} available slots in UTC+5:30 timezone",
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
    Create a new calendar event in UTC+5:30 timezone.
    
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
        # Parse datetime strings and ensure they're in UTC+5:30 timezone
        start_dt = datetime.fromisoformat(start_datetime)
        end_dt = datetime.fromisoformat(end_datetime)
        
        # Ensure timezone awareness
        if start_dt.tzinfo is None:
            start_dt = UTC_5_30_TIMEZONE.localize(start_dt)
        else:
            start_dt = start_dt.astimezone(UTC_5_30_TIMEZONE)
            
        if end_dt.tzinfo is None:
            end_dt = UTC_5_30_TIMEZONE.localize(end_dt)
        else:
            end_dt = end_dt.astimezone(UTC_5_30_TIMEZONE)
        
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
                "message": f"Successfully created event '{title}' in UTC+5:30 timezone",
                "event": {
                    "id": event.get('id'),
                    "title": title,
                    "start": start_dt.strftime("%Y-%m-%d %I:%M %p UTC+5:30"),
                    "end": end_dt.strftime("%Y-%m-%d %I:%M %p UTC+5:30"),
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
    Get busy time slots to understand calendar conflicts in UTC+5:30 timezone.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        JSON string with busy time slots in UTC+5:30
    """
    try:
        # Parse dates and set to start/end of day in UTC+5:30 timezone
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        start_dt = UTC_5_30_TIMEZONE.localize(start_dt.replace(hour=0, minute=0, second=0))
        
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        end_dt = UTC_5_30_TIMEZONE.localize(end_dt.replace(hour=23, minute=59, second=59))
        
        # Get busy times
        busy_times = calendar_client.get_busy_times(start_dt, end_dt)
        
        # Format the response with UTC+5:30 timezone
        formatted_busy = []
        for busy in busy_times:
            start_time = calendar_client._parse_datetime_with_timezone(busy['start'])
            end_time = calendar_client._parse_datetime_with_timezone(busy['end'])
            formatted_busy.append({
                "start": busy['start'],
                "end": busy['end'],
                "start_formatted": start_time.strftime("%A, %B %d at %I:%M %p UTC+5:30"),
                "end_formatted": end_time.strftime("%I:%M %p UTC+5:30"),
                "summary": busy.get('summary', 'Busy')
            })
        
        return json.dumps({
            "status": "success",
            "busy_times": formatted_busy,
            "count": len(formatted_busy),
            "timezone": "UTC+5:30 (Indian Standard Time)"
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error getting busy times: {str(e)}",
            "busy_times": []
        })


# Export all tools for the agent
calendar_tools = [check_availability, create_calendar_event, get_busy_times]