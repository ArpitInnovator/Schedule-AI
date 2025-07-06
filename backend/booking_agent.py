import os
from typing import Dict, Any, List, Optional
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage
from .agent_tools import calendar_tools


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
            model="gemini-pro",
            google_api_key=api_key,
            temperature=0.1,
            convert_system_message_to_human=True
        )
    
    def _setup_agent(self):
        """Setup the agent with tools and prompt."""
        
        # System prompt for the booking agent
        system_prompt = """You are a helpful calendar booking assistant. Your job is to help users book appointments in their Google Calendar through natural conversation.

Key capabilities:
1. Check calendar availability for requested dates/times
2. Suggest alternative time slots when requested times are not available
3. Create calendar events when the user confirms a booking
4. Handle scheduling requests naturally and conversationally

Important guidelines:
- Always be friendly and professional
- When a user asks to book a meeting, first check availability for their requested time
- If the requested time is not available, proactively suggest alternative slots
- Before creating any calendar event, confirm the details with the user (title, time, duration, description)
- Ask for clarification if booking details are missing (e.g., meeting title, duration)
- Default meeting duration is 60 minutes unless specified otherwise
- Only suggest time slots during business hours (9 AM - 5 PM) unless user specifically requests otherwise

Current date context: Use today's date as a reference point when users mention relative dates like "tomorrow", "next week", etc.

Be conversational and helpful. If the user's request is unclear, ask follow-up questions to get the necessary details for booking.
"""

        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad")
        ])
        
        # Create the agent
        agent = create_openai_functions_agent(
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
            max_iterations=3
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
            for msg in chat_history:
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
            return {
                "success": False,
                "response": f"I apologize, but I encountered an error while processing your request. Please try again or rephrase your question.",
                "intermediate_steps": [],
                "error": str(e)
            }
    
    def get_greeting(self) -> str:
        """Get a greeting message for new conversations."""
        return """Hi there! I'm your calendar booking assistant. I can help you:

📅 Check your calendar availability
⏰ Schedule new meetings and appointments  
🔄 Suggest alternative time slots
✅ Confirm and create calendar events

What would you like to schedule today? Just let me know the details like:
- What type of meeting/appointment
- Preferred date and time
- Duration (if different from 1 hour)
- Any additional details

How can I help you schedule something?"""


# Create a global instance
booking_agent = BookingAgent()