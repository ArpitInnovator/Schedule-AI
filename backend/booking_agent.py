import os
from typing import Dict, Any, List, Optional
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from agent_tools import calendar_tools


class BookingAgent:
    def __init__(self):
        """Initialize the booking agent with Gemini LLM and calendar tools."""
        self.llm = self._setup_llm()
        self.agent_executor = self._setup_agent()
        
    def _setup_llm(self):
        """Setup the Gemini LLM."""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
            
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0.1
        )
    
    def _setup_agent(self):
        """Setup the agent with tools and prompt."""
        
        # System prompt for the booking agent with Indian timezone
        system_prompt = """You are a helpful calendar booking assistant configured for Indian timezone (IST). Your job is to help users book appointments in their Google Calendar through natural conversation.

Key capabilities:
1. Check calendar availability for requested dates/times using the check_availability tool
2. Suggest alternative time slots when requested times are not available
3. Create calendar events when the user confirms a booking using the create_calendar_event tool
4. Handle scheduling requests naturally and conversationally

Important guidelines:
- Always be friendly and professional
- All times are in Indian Standard Time (IST) - UTC+5:30
- When a user asks to book a meeting, first check availability for their requested time using the check_availability tool
- If the requested time is not available, proactively suggest alternative slots from the availability results
- Before creating any calendar event, confirm the details with the user (title, time, duration, description)
- Ask for clarification if booking details are missing (e.g., meeting title, duration)
- Default meeting duration is 60 minutes unless specified otherwise
- Only suggest time slots during business hours (9 AM - 6 PM IST) unless user specifically requests otherwise
- When creating events, use the create_calendar_event tool with proper ISO format dates
- Always mention IST when discussing times to avoid confusion

Current date context: Today is 2024-01-20. Use this as reference for relative dates like "tomorrow", "next week", etc.

When checking availability:
- Use YYYY-MM-DD format for dates when calling check_availability
- For times like "2 PM tomorrow", convert to ISO format like "2024-01-21T14:00:00" for create_calendar_event
- All times will be interpreted as IST

Be conversational and helpful. If the user's request is unclear, ask follow-up questions to get the necessary details for booking.
"""

        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad")
        ])
        
        # Create the agent using the new syntax
        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=calendar_tools,
            prompt=prompt
        )
        
        # Create the executor
        return AgentExecutor(
            agent=agent,
            tools=calendar_tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            return_intermediate_steps=True
        )
    
    def process_message(self, message: str, chat_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Process a user message and return the agent's response.
        
        Args:
            message: User's message
            chat_history: Previous conversation history
            
        Returns:
            Dictionary with agent response and metadata
        """
        if chat_history is None:
            chat_history = []
            
        try:
            # Format chat history for LangChain
            formatted_history = []
            for msg in chat_history[-10:]:  # Keep last 10 messages for context
                if msg["role"] == "user":
                    formatted_history.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    formatted_history.append(AIMessage(content=msg["content"]))
            
            # Process the message with the agent
            result = self.agent_executor.invoke({
                "input": message,
                "chat_history": formatted_history
            })
            
            return {
                "success": True,
                "response": result["output"],
                "intermediate_steps": result.get("intermediate_steps", []),
                "error": None
            }
            
        except Exception as e:
            print(f"Error in agent processing: {e}")
            return {
                "success": False,
                "response": f"I apologize, but I encountered an error while processing your request: {str(e)}. Please try again or rephrase your question.",
                "intermediate_steps": [],
                "error": str(e)
            }
    
    def get_greeting(self) -> str:
        """Get a greeting message for new conversations."""
        return """Hi there! I'm your AI calendar booking assistant configured for Indian timezone (IST). I can help you:

📅 **Check your calendar availability** - I'll look at your real calendar to find free time slots in IST
⏰ **Schedule new meetings and appointments** - I'll create actual events in your Google Calendar in Indian time
🔄 **Suggest alternative time slots** - If your preferred time isn't available, I'll find other options
✅ **Confirm and create calendar events** - I'll handle all the booking details

**Important:** All times are in Indian Standard Time (IST) - UTC+5:30

What would you like to schedule today? Just let me know details like:
- What type of meeting/appointment (e.g., "Team meeting", "Doctor appointment")
- Preferred date and time (e.g., "Tomorrow at 2 PM IST", "Next Friday morning")
- Duration (defaults to 1 hour if not specified)
- Any additional details or attendees

For example, you could say:
- "I need to schedule a team meeting for tomorrow at 2 PM IST"
- "Check my availability for next Monday"
- "Book a 30-minute call with John on Friday afternoon"

How can I help you schedule something?"""


# Create a global instance
try:
    booking_agent = BookingAgent()
    print("✅ Booking agent initialized successfully with Indian timezone")
except Exception as e:
    print(f"❌ Failed to initialize booking agent: {e}")
    booking_agent = None