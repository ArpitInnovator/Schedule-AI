"""Google Calendar client for managing appointments."""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import settings


class CalendarClient:
    """Client for interacting with Google Calendar API."""
    
    def __init__(self):
        """Initialize the Google Calendar client with service account credentials."""
        self.calendar_id = settings.google_calendar_id
        self.service = self._build_service()
        self.timezone = pytz.timezone('UTC')  # Default to UTC, can be made configurable
    
    def _build_service(self):
        """Build the Google Calendar service using service account credentials."""
        credentials = service_account.Credentials.from_service_account_file(
            settings.google_calendar_credentials_path,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        return build('calendar', 'v3', credentials=credentials)
    
    def check_availability(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, datetime]]:
        """
        Check calendar availability for a given time range.
        
        Args:
            start_time: Start time for checking availability
            end_time: End time for checking availability
            
        Returns:
            List of busy time slots within the requested range
        """
        try:
            # Format times for API
            timeMin = start_time.isoformat()
            timeMax = end_time.isoformat()
            
            # Query for busy times
            body = {
                "timeMin": timeMin,
                "timeMax": timeMax,
                "items": [{"id": self.calendar_id}],
                "timeZone": str(self.timezone)
            }
            
            events_result = self.service.freebusy().query(body=body).execute()
            busy_times = events_result['calendars'][self.calendar_id]['busy']
            
            # Convert to datetime objects
            busy_slots = []
            for busy in busy_times:
                busy_slots.append({
                    'start': datetime.fromisoformat(busy['start'].replace('Z', '+00:00')),
                    'end': datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                })
            
            return busy_slots
            
        except HttpError as error:
            print(f"An error occurred checking availability: {error}")
            return []
    
    def find_available_slots(
        self,
        date: datetime,
        duration_minutes: int = 30,
        start_hour: int = 9,
        end_hour: int = 17,
        slot_interval_minutes: int = 30
    ) -> List[Tuple[datetime, datetime]]:
        """
        Find available time slots on a given date.
        
        Args:
            date: The date to check for availability
            duration_minutes: Duration of the appointment in minutes
            start_hour: Start of business hours (24-hour format)
            end_hour: End of business hours (24-hour format)
            slot_interval_minutes: Interval between potential slots
            
        Returns:
            List of available time slots as (start, end) tuples
        """
        # Set up the day's time range
        day_start = date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        day_end = date.replace(hour=end_hour, minute=0, second=0, microsecond=0)
        
        # Get busy times for the day
        busy_times = self.check_availability(day_start, day_end)
        
        # Generate all possible slots
        available_slots = []
        current_time = day_start
        
        while current_time + timedelta(minutes=duration_minutes) <= day_end:
            slot_end = current_time + timedelta(minutes=duration_minutes)
            
            # Check if this slot conflicts with any busy times
            is_available = True
            for busy in busy_times:
                # Check for overlap
                if not (slot_end <= busy['start'] or current_time >= busy['end']):
                    is_available = False
                    break
            
            if is_available:
                available_slots.append((current_time, slot_end))
            
            current_time += timedelta(minutes=slot_interval_minutes)
        
        return available_slots
    
    def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        attendees: Optional[List[str]] = None
    ) -> Dict:
        """
        Create a calendar event.
        
        Args:
            summary: Event title/summary
            start_time: Event start time
            end_time: Event end time
            description: Optional event description
            attendees: Optional list of attendee email addresses
            
        Returns:
            Created event details
        """
        try:
            event = {
                'summary': summary,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': str(self.timezone),
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': str(self.timezone),
                },
            }
            
            if description:
                event['description'] = description
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            # Create the event
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            return {
                'id': created_event.get('id'),
                'link': created_event.get('htmlLink'),
                'summary': created_event.get('summary'),
                'start': start_time,
                'end': end_time
            }
            
        except HttpError as error:
            print(f"An error occurred creating event: {error}")
            raise
    
    def get_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Get calendar events within a time range.
        
        Args:
            start_time: Start time for event search (defaults to now)
            end_time: End time for event search
            max_results: Maximum number of events to return
            
        Returns:
            List of calendar events
        """
        try:
            if not start_time:
                start_time = datetime.now(self.timezone)
            
            # Call the Calendar API
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_time.isoformat(),
                timeMax=end_time.isoformat() if end_time else None,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Process events
            processed_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                processed_events.append({
                    'id': event.get('id'),
                    'summary': event.get('summary', 'No title'),
                    'start': start,
                    'end': end,
                    'description': event.get('description', '')
                })
            
            return processed_events
            
        except HttpError as error:
            print(f"An error occurred fetching events: {error}")
            return []