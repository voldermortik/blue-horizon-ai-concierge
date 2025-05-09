from typing import Dict, Any, Optional, List, Union
from autogen import ConversableAgent
from blue_horizon.agents.config import OPENAI_CONFIG


class BaseConciergAgent(ConversableAgent):
    """Base agent class for all concierge agents in the simplified system."""

    def __init__(
        self,
        name: str,
        description: str,
        instructions: str,
        llm_config: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """Initialize the base concierge agent."""
        self.agent_name = name
        self.description = description

        # Use default OpenAI config if none provided
        if llm_config is None:
            llm_config = OPENAI_CONFIG

        system_message = f"""You are {name}, an agent in the Blue Horizon AI Concierge system.
        
        Role Description:
        {description}
        
        Instructions:
        {instructions}
        
        Always maintain a professional and helpful demeanor while interacting with guests and other agents.
        Focus on your specific role while coordinating with other agents when needed.
        """

        super().__init__(
            name=name, system_message=system_message, llm_config=llm_config, **kwargs
        )

        # Initialize conversation memory
        self.conversation_memory = []

    def remember_interaction(
        self, message: str, response: str, metadata: Optional[Dict] = None
    ):
        """Store an interaction in the agent's memory."""
        self.conversation_memory.append(
            {"message": message, "response": response, "metadata": metadata or {}}
        )

        # Keep only last 10 interactions to prevent memory bloat
        if len(self.conversation_memory) > 10:
            self.conversation_memory = self.conversation_memory[-10:]

    def get_relevant_memory(self, query: str) -> List[Dict]:
        """Get relevant past interactions based on a query."""
        # Simple relevance matching - could be enhanced with embeddings
        relevant = []
        for memory in self.conversation_memory:
            if any(word in memory["message"].lower() for word in query.lower().split()):
                relevant.append(memory)
        return relevant

    async def _process_message(
        self, message: Union[str, Dict], sender: Optional[Any] = None
    ) -> str:
        """Process an incoming message and generate a response."""
        try:
            # Get message text
            message_text = message if isinstance(message, str) else str(message)

            # Get relevant past interactions
            relevant_memory = self.get_relevant_memory(message_text)

            # Generate response using the LLM
            response = await self.generate_response(message_text, relevant_memory)

            # Store the interaction
            self.remember_interaction(message_text, response)

            return response

        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            self.remember_interaction(str(message), error_msg, {"error": str(e)})
            return error_msg

    async def generate_response(self, message: str, context: List[Dict]) -> str:
        """Generate a response to a message using the agent's LLM.

        Args:
            message: The input message to respond to
            context: List of relevant past interactions

        Returns:
            str: The generated response
        """
        # Format context into a string
        context_str = ""
        if context:
            context_str = "\nRelevant past interactions:\n"
            for interaction in context:
                context_str += f"User: {interaction['message']}\n"
                context_str += f"Response: {interaction['response']}\n"

        # Combine message with context
        full_message = f"{message}\n{context_str}" if context_str else message

        # Use the built-in reply functionality of ConversableAgent
        async for response in self.generate_reply(
            messages=[{"role": "user", "content": full_message}],
            sender=None,
        ):
            if response:
                return response

        return "I apologize, but I couldn't generate a response."
