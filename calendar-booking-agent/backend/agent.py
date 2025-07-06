"""LangChain agent with calendar tools for appointment booking."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
from dateutil import parser
from dateutil.relativedelta import relativedelta
import pytz

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain_core.pydantic_v1 import BaseModel, Field

from calendar_client import CalendarClient
from config import settings


class BookingRequest(BaseModel):
    """Schema for appointment booking parameters."""
    summary: str = Field(description="Title or summary of the appointment")
    date: str = Field(description="Date for the appointment (e.g., 'tomorrow', '2024-01-15', 'next Monday')")
    time: str = Field(description="Time for the appointment (e.g., '2pm', '14:00', 'afternoon')")
    duration_minutes: int = Field(default=30, description="Duration of the appointment in minutes")
    description: Optional[str] = Field(default=None, description="Additional description or notes")


class CalendarTools:
    """Calendar tools for the booking agent."""
    
    def __init__(self):
        self.calendar = CalendarClient()
        self.timezone = pytz.timezone('UTC')
    
    def _parse_datetime(self, date_str: str, time_str: str) -> datetime:
        """Parse natural language date and time into datetime object."""
        # Handle relative dates
        today = datetime.now(self.timezone)
        
        # Parse date
        date_lower = date_str.lower()
        if date_lower == 'today':
            date = today.date()
        elif date_lower == 'tomorrow':
            date = (today + timedelta(days=1)).date()
        elif 'next' in date_lower:
            # Simple parsing for "next Monday", etc.
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for i, day in enumerate(days):
                if day in date_lower:
                    days_ahead = i - today.weekday()
                    if days_ahead <= 0:  # Target day already happened this week
                        days_ahead += 7
                    date = (today + timedelta(days=days_ahead)).date()
                    break
            else:
                # Try to parse as regular date
                date = parser.parse(date_str).date()
        else:
            # Try to parse as regular date
            date = parser.parse(date_str).date()
        
        # Parse time
        time_lower = time_str.lower()
        if 'morning' in time_lower:
            time = datetime.strptime('09:00', '%H:%M').time()
        elif 'afternoon' in time_lower:
            time = datetime.strptime('14:00', '%H:%M').time()
        elif 'evening' in time_lower:
            time = datetime.strptime('18:00', '%H:%M').time()
        else:
            # Parse actual time
            try:
                time = parser.parse(time_str).time()
            except:
                # Default to 9 AM if parsing fails
                time = datetime.strptime('09:00', '%H:%M').time()
        
        # Combine date and time
        dt = datetime.combine(date, time)
        return self.timezone.localize(dt)
    
    def check_availability(self, date: str, time: str, duration_minutes: int = 30) -> str:
        """
        Check if a specific time slot is available.
        
        Args:
            date: Date to check (e.g., 'tomorrow', '2024-01-15')
            time: Time to check (e.g., '2pm', '14:00')
            duration_minutes: Duration of the appointment in minutes
            
        Returns:
            Availability status and suggestions if unavailable
        """
        try:
            start_time = self._parse_datetime(date, time)
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Check for conflicts
            busy_times = self.calendar.check_availability(start_time, end_time)
            
            if not busy_times:
                return f"✅ The time slot from {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%H:%M')} is available."
            else:
                # Find alternative slots
                available_slots = self.calendar.find_available_slots(
                    start_time.replace(hour=0, minute=0, second=0),
                    duration_minutes=duration_minutes
                )
                
                suggestions = []
                for slot_start, slot_end in available_slots[:3]:  # Show top 3 alternatives
                    suggestions.append(f"• {slot_start.strftime('%H:%M')} - {slot_end.strftime('%H:%M')}")
                
                suggestion_text = "\n".join(suggestions) if suggestions else "No available slots found on this day."
                
                return f"❌ The requested time slot is not available. Here are some alternative times on {start_time.strftime('%Y-%m-%d')}:\n{suggestion_text}"
                
        except Exception as e:
            return f"Error checking availability: {str(e)}"
    
    def book_appointment(
        self,
        summary: str,
        date: str,
        time: str,
        duration_minutes: int = 30,
        description: Optional[str] = None
    ) -> str:
        """
        Book an appointment on the calendar.
        
        Args:
            summary: Title of the appointment
            date: Date for the appointment
            time: Time for the appointment
            duration_minutes: Duration in minutes
            description: Optional description
            
        Returns:
            Booking confirmation or error message
        """
        try:
            start_time = self._parse_datetime(date, time)
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Check availability first
            busy_times = self.calendar.check_availability(start_time, end_time)
            if busy_times:
                return "❌ Cannot book: The requested time slot is already occupied. Please check availability first."
            
            # Create the event
            event = self.calendar.create_event(
                summary=summary,
                start_time=start_time,
                end_time=end_time,
                description=description
            )
            
            return f"✅ Appointment booked successfully!\n\n" \
                   f"📅 **{event['summary']}**\n" \
                   f"🕒 {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}\n" \
                   f"🔗 [Calendar Link]({event['link']})"
                   
        except Exception as e:
            return f"Error booking appointment: {str(e)}"
    
    def list_upcoming_appointments(self, days_ahead: int = 7) -> str:
        """
        List upcoming appointments.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of upcoming appointments
        """
        try:
            start_time = datetime.now(self.timezone)
            end_time = start_time + timedelta(days=days_ahead)
            
            events = self.calendar.get_events(start_time, end_time)
            
            if not events:
                return "No upcoming appointments found."
            
            appointments = ["📅 **Upcoming Appointments:**\n"]
            for event in events:
                start = parser.parse(event['start'])
                appointments.append(
                    f"• {start.strftime('%Y-%m-%d %H:%M')} - {event['summary']}"
                )
            
            return "\n".join(appointments)
            
        except Exception as e:
            return f"Error listing appointments: {str(e)}"


def create_booking_agent():
    """Create the LangChain agent with calendar tools."""
    # Initialize tools
    calendar_tools = CalendarTools()
    
    # Define tools
    tools = [
        Tool(
            name="check_calendar_availability",
            func=calendar_tools.check_availability,
            description="Check if a specific time slot is available on the calendar. "
                       "Input should include date (e.g., 'tomorrow', '2024-01-15'), "
                       "time (e.g., '2pm', '14:00'), and duration in minutes."
        ),
        Tool(
            name="book_calendar_appointment",
            func=calendar_tools.book_appointment,
            description="Book an appointment on the calendar. "
                       "Input should include summary/title, date, time, duration in minutes, "
                       "and optional description. Always check availability first!"
        ),
        Tool(
            name="list_upcoming_appointments",
            func=calendar_tools.list_upcoming_appointments,
            description="List upcoming appointments from the calendar. "
                       "Input can include number of days to look ahead (default 7)."
        )
    ]
    
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=settings.google_api_key,
        temperature=0.7,
        convert_system_message_to_human=True
    )
    
    # Create prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful appointment booking assistant. Your role is to help users schedule appointments on their calendar.

Key responsibilities:
1. Greet users warmly and ask how you can help with their scheduling needs
2. When users want to book an appointment, gather the following information:
   - Purpose/title of the appointment
   - Preferred date and time
   - Duration (default to 30 minutes if not specified)
   - Any additional notes or description
3. ALWAYS check availability before booking
4. If the requested time is unavailable, suggest alternative slots
5. Confirm all details before making the booking
6. Be conversational and natural - don't just list information

Remember:
- Parse natural language dates like "tomorrow", "next Monday", etc.
- Parse natural language times like "2pm", "afternoon", etc.
- Always be helpful and suggest alternatives if needed
- Confirm successful bookings with all details"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    # Create agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # Create executor with memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True
    )
    
    return agent_executor


# Singleton instance
booking_agent = None


def get_booking_agent():
    """Get or create the booking agent instance."""
    global booking_agent
    if booking_agent is None:
        booking_agent = create_booking_agent()
    return booking_agent