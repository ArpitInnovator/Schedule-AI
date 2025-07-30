import os
import json
import pytz
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from google.auth.transport.requests import Request # type: ignore
from google.oauth2 import service_account # type: ignore
from googleapiclient.discovery import build # type: ignore
from googleapiclient.errors import HttpError # type: ignore


class CalendarClient:
    def __init__(self):
        """Initialize the Google Calendar client with service account credentials."""
        self.service = None
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
        # Set Indian timezone (IST)
        self.timezone = pytz.timezone('Asia/Kolkata')
        self._setup_service()
    
    def _setup_service(self):
        """Set up the Google Calendar service with service account credentials."""
        try:
            # Load service account credentials from environment variable
            service_account_info = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
            if not service_account_info:
                raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON environment variable is required")
            
            # Parse the JSON credentials
            credentials_dict = json.loads(service_account_info)
            
            # Create credentials object
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict,
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            
            # Build the service
            self.service = build('calendar', 'v3', credentials=credentials)
            
        except Exception as e:
            print(f"Error setting up Calendar service: {e}")
            self.service = None
    
    def _parse_datetime_with_timezone(self, dt_str: str) -> datetime:
        """Parse datetime string and convert to Indian timezone."""
        try:
            # Handle different datetime formats
            if 'Z' in dt_str:
                dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(dt_str)
            
            # Convert to Indian timezone if it's timezone-aware
            if dt.tzinfo is not None:
                return dt.astimezone(self.timezone)
            else:
                # Assume UTC if no timezone info
                return pytz.UTC.localize(dt).astimezone(self.timezone)
        except Exception as e:
            print(f"Error parsing datetime {dt_str}: {e}")
            return datetime.now(self.timezone)
    
    def _ensure_timezone_aware(self, dt: datetime) -> datetime:
        """Ensure datetime is timezone-aware and in Indian timezone."""
        if dt.tzinfo is None:
            # If naive datetime, assume it's in Indian time
            return self.timezone.localize(dt)
        else:
            # If timezone-aware, convert to Indian time
            return dt.astimezone(self.timezone)
    
    def get_busy_times(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Get busy time slots between start_date and end_date.
        
        Args:
            start_date: Start of the time range to check
            end_date: End of the time range to check
            
        Returns:
            List of busy time slots with start and end times
        """
        if not self.service:
            # Return mock data for development with Indian timezone
            start_ist = self._ensure_timezone_aware(start_date)
            return [
                {
                    'start': start_ist.replace(hour=10, minute=0).isoformat(),
                    'end': start_ist.replace(hour=11, minute=0).isoformat(),
                    'summary': 'Existing meeting'
                }
            ]
        
        try:
            # Ensure dates are timezone-aware and in IST
            start_ist = self._ensure_timezone_aware(start_date)
            end_ist = self._ensure_timezone_aware(end_date)
            
            # Get events from the calendar
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_ist.isoformat(),
                timeMax=end_ist.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            busy_times = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                busy_times.append({
                    'start': start,
                    'end': end,
                    'summary': event.get('summary', 'Busy')
                })
            
            return busy_times
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []
    
    def find_available_slots(self, start_date: datetime, end_date: datetime, 
                           duration_minutes: int = 60, 
                           business_hours_only: bool = True) -> List[Dict]:
        """
        Find available time slots within the given date range.
        
        Args:
            start_date: Start of the search range
            end_date: End of the search range
            duration_minutes: Duration of the desired meeting in minutes
            business_hours_only: If True, only suggest slots during business hours (9 AM - 6 PM IST)
            
        Returns:
            List of available time slots
        """
        # Ensure dates are in Indian timezone
        start_ist = self._ensure_timezone_aware(start_date)
        end_ist = self._ensure_timezone_aware(end_date)
        
        busy_times = self.get_busy_times(start_ist, end_ist)
        available_slots = []
        
        # Convert busy times to datetime objects with Indian timezone
        busy_periods = []
        for busy in busy_times:
            busy_start = self._parse_datetime_with_timezone(busy['start'])
            busy_end = self._parse_datetime_with_timezone(busy['end'])
            busy_periods.append((busy_start, busy_end))
        
        # Sort busy periods by start time
        busy_periods.sort(key=lambda x: x[0])
        
        # Find gaps between busy periods
        current_time = start_ist
        
        for busy_start, busy_end in busy_periods:
            # Check if there's a gap before this busy period
            if current_time < busy_start:
                # Calculate available time
                available_duration = (busy_start - current_time).total_seconds() / 60
                if available_duration >= duration_minutes:
                    # Generate slots in this gap
                    slot_start = current_time
                    while slot_start + timedelta(minutes=duration_minutes) <= busy_start:
                        # Check business hours in Indian time (9 AM - 6 PM IST)
                        if not business_hours_only or (9 <= slot_start.hour < 18):
                            available_slots.append({
                                'start': slot_start.isoformat(),
                                'end': (slot_start + timedelta(minutes=duration_minutes)).isoformat(),
                                'duration_minutes': duration_minutes
                            })
                        slot_start += timedelta(minutes=duration_minutes)  # Use meeting duration instead of 30-minute intervals
            
            current_time = max(current_time, busy_end)
        
        # Check for availability after the last busy period
        if current_time < end_ist:
            available_duration = (end_ist - current_time).total_seconds() / 60
            if available_duration >= duration_minutes:
                slot_start = current_time
                while slot_start + timedelta(minutes=duration_minutes) <= end_ist:
                    # Check business hours in Indian time (9 AM - 6 PM IST)
                    if not business_hours_only or (9 <= slot_start.hour < 18):
                        available_slots.append({
                            'start': slot_start.isoformat(),
                            'end': (slot_start + timedelta(minutes=duration_minutes)).isoformat(),
                            'duration_minutes': duration_minutes
                        })
                    slot_start += timedelta(minutes=duration_minutes)  # Use meeting duration instead of 30-minute intervals
        
        return available_slots[:10]  # Return top 10 slots
    
    def create_event(self, title: str, start_time: datetime, end_time: datetime, 
                    description: str = "") -> Optional[Dict]:
        """
        Create a new calendar event with Indian timezone.
        
        Args:
            title: Event title
            start_time: Event start time
            end_time: Event end time
            description: Event description
            
        Returns:
            Created event details or mock data
        """
        if not self.service:
            # Return mock confirmation for development with Indian timezone
            start_ist = self._ensure_timezone_aware(start_time)
            end_ist = self._ensure_timezone_aware(end_time)
            return {
                'id': 'mock_event_id',
                'summary': title,
                'start': {'dateTime': start_ist.isoformat()},
                'end': {'dateTime': end_ist.isoformat()},
                'htmlLink': 'https://calendar.google.com/mock-event',
                'status': 'confirmed'
            }
        
        try:
            # Ensure times are timezone-aware and in Indian timezone
            start_ist = self._ensure_timezone_aware(start_time)
            end_ist = self._ensure_timezone_aware(end_time)
            
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_ist.isoformat(),
                    'timeZone': 'Asia/Kolkata',  # Indian timezone
                },
                'end': {
                    'dateTime': end_ist.isoformat(),
                    'timeZone': 'Asia/Kolkata',  # Indian timezone
                },
            }
            
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            return created_event
            
        except HttpError as error:
            print(f"An error occurred creating event: {error}")
            return None