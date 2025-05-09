"""User proxy for handling interactions between users and the agent system."""

from typing import Dict, Any, Optional
from datetime import datetime

from autogen import UserProxyAgent

from blue_horizon.agents.definitions import USER_PROXY


class ConciergUserProxy(UserProxyAgent):
    """User proxy agent for the Blue Horizon AI Concierge system."""

    def __init__(self, **kwargs):
        """Initialize the user proxy agent."""
        super().__init__(
            name=USER_PROXY.name,
            system_message=f"""
            {USER_PROXY.description}
            
            Your responsibilities include:
            1. Interface between human users and the agent system
            2. Format and validate user inputs
            3. Ensure clear and professional communication
            4. Maintain conversation context
            
            Guidelines:
            - Always maintain a professional and courteous tone
            - Format requests appropriately for other agents
            - Provide clear feedback to users
            - Handle errors gracefully
            """,
            human_input_mode=USER_PROXY.human_input_mode,
            max_consecutive_auto_reply=USER_PROXY.max_consecutive_auto_reply,
            llm_config=USER_PROXY.llm_config,
            **kwargs,
        )

        # Initialize session state
        self.session_start = datetime.now()
        self.conversation_history = []

    def format_message(self, message: str) -> str:
        """Format a user message for the agent system."""
        return message.strip()

    def remember_interaction(self, message: str, response: str):
        """Store an interaction in the conversation history."""
        self.conversation_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "message": message,
                "response": response,
            }
        )

    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session."""
        return {
            "session_start": self.session_start.isoformat(),
            "interaction_count": len(self.conversation_history),
            "last_interaction": (
                self.conversation_history[-1] if self.conversation_history else None
            ),
        }

    async def handle_error(self, error: Exception) -> str:
        """Handle errors gracefully and return user-friendly messages."""
        error_msg = str(error)

        # Common error responses
        responses = {
            "timeout": "I apologize, but the request timed out. Please try again.",
            "connection": "There seems to be a connection issue. Please try again in a moment.",
            "validation": "I couldn't process that request. Please check the format and try again.",
        }

        # Match error type to response
        for error_type, response in responses.items():
            if error_type.lower() in error_msg.lower():
                return response

        # Default error message
        return "I encountered an issue processing your request. Please try again or rephrase your question."
