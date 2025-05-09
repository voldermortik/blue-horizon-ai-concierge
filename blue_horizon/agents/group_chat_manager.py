"""Group chat manager for coordinating multi-agent conversations."""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime

import autogen
from autogen import Agent, GroupChat, GroupChatManager as AutoGenGroupChatManager

from blue_horizon.agents.base_agent import BaseConciergAgent
from blue_horizon.agents.definitions import GROUP_CHAT_MANAGER, AGENT_SYSTEM_CONFIG


class GroupChatManager(AutoGenGroupChatManager):
    """Manager for coordinating conversations between multiple agents."""

    def __init__(self, groupchat: GroupChat, **kwargs):
        """Initialize the group chat manager."""
        super().__init__(
            groupchat=groupchat,
            name=GROUP_CHAT_MANAGER.name,
            system_message=f"""
            {GROUP_CHAT_MANAGER.description}
            
            Your responsibilities include:
            1. Route messages to appropriate agents based on their capabilities
            2. Maintain conversation flow and context
            3. Ensure all necessary agents are involved in complex tasks
            4. Prevent redundant or conflicting responses
            5. Summarize conversations when needed
            
            Guidelines:
            - Always route requests to the most appropriate agent(s)
            - Maintain conversation history for context
            - Ensure proper turn-taking between agents
            - Intervene if the conversation goes off-track
            - Summarize key points and decisions
            """,
            llm_config=GROUP_CHAT_MANAGER.llm_config,
            **kwargs,
        )

        self.agent_capabilities = {}
        self._register_agent_capabilities()

    def _register_agent_capabilities(self):
        """Register capabilities of all agents in the group chat."""
        for agent in self.groupchat.agents:
            if hasattr(agent, "get_capabilities"):
                self.agent_capabilities[agent.name] = agent.get_capabilities()

    def select_speaker(
        self, message: str, sender: Agent, speaking_agents: List[Agent]
    ) -> Optional[Agent]:
        """Select the next speaker based on message content and agent capabilities."""
        # If sender is user_proxy, route based on content
        if sender.name == "UserProxy":
            return self._route_user_request(message, speaking_agents)

        # If in middle of task, let current agent continue or hand off explicitly
        if speaking_agents and speaking_agents[-1] != sender:
            last_speaker = speaking_agents[-1]
            if self._should_continue_current_task(message, last_speaker):
                return last_speaker

        # Default to super() implementation
        return super().select_speaker(message, sender, speaking_agents)

    def _route_user_request(
        self, message: str, available_agents: List[Agent]
    ) -> Optional[Agent]:
        """Route user request to the most appropriate agent."""
        message = message.lower()

        # Score each agent's suitability for the request
        agent_scores = {}
        for agent in available_agents:
            if agent.name in self.agent_capabilities:
                score = self._calculate_agent_suitability(
                    message, self.agent_capabilities[agent.name]
                )
                agent_scores[agent] = score

        # Select agent with highest score
        if agent_scores:
            return max(agent_scores.items(), key=lambda x: x[1])[0]

        return None

    def _calculate_agent_suitability(
        self, message: str, capabilities: Dict[str, Any]
    ) -> float:
        """Calculate how suitable an agent is for handling a message."""
        score = 0.0

        # Check each capability against the message
        if "can_handle" in capabilities:
            for capability in capabilities["can_handle"]:
                # Convert capability to keywords
                keywords = capability.replace("_", " ").split()
                # Check each keyword
                for keyword in keywords:
                    if keyword in message:
                        score += 1.0

        return score

    def _should_continue_current_task(self, message: str, current_agent: Agent) -> bool:
        """Determine if current task should continue with the same agent."""
        # Check if message indicates task completion
        completion_indicators = ["done", "completed", "finished", "thank you", "thanks"]
        if any(indicator in message.lower() for indicator in completion_indicators):
            return False

        # Check if message requests different service
        if current_agent.name in self.agent_capabilities:
            current_capabilities = self.agent_capabilities[current_agent.name]
            # If message doesn't match current agent's capabilities, switch
            if self._calculate_agent_suitability(message, current_capabilities) == 0:
                return False

        return True

    def summarize_conversation(self, messages: List[Dict[str, Any]]) -> str:
        """Summarize the conversation history."""
        summary = []
        current_topic = None

        for msg in messages:
            sender = msg.get("sender", "Unknown")
            content = msg.get("content", "")

            # Detect topic changes
            new_topic = self._detect_topic(content)
            if new_topic != current_topic:
                current_topic = new_topic
                summary.append(f"\nTopic: {current_topic}")

            # Add key points
            key_points = self._extract_key_points(content)
            if key_points:
                summary.append(f"{sender}: {key_points}")

        return "\n".join(summary)

    def _detect_topic(self, message: str) -> str:
        """Detect the topic of a message."""
        # TODO: Implement topic detection logic
        return "General Discussion"

    def _extract_key_points(self, message: str) -> str:
        """Extract key points from a message."""
        # TODO: Implement key points extraction
        return message[:100] + "..." if len(message) > 100 else message
