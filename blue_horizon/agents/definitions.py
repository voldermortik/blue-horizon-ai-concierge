"""Agent definitions for the Blue Horizon AI Concierge system.

This module defines all agents used in the system, including their roles,
responsibilities, and configurations.
"""

from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class AgentRole(Enum):
    """Enum defining the possible roles for agents in the system."""

    USER_PROXY = "user_proxy"
    GROUP_MANAGER = "group_manager"
    BOOKING = "booking"
    CUSTOMER_SERVICE = "customer_service"
    FACILITIES = "facilities"
    CONCIERGE = "concierge"
    STAFF_COORDINATOR = "staff_coordinator"
    ANALYTICS = "analytics"
    ORCHESTRATOR = "orchestrator"


@dataclass
class AgentConfig:
    """Configuration for an individual agent."""

    role: AgentRole
    name: str
    description: str
    llm_config: Dict
    tools: List[str]
    human_input_mode: str = "NEVER"
    max_consecutive_auto_reply: int = 10


# System-level agents
USER_PROXY = AgentConfig(
    role=AgentRole.USER_PROXY,
    name="UserProxy",
    description="Interface between human users and the agent system. Handles all direct user interactions.",
    llm_config={
        "temperature": 0.7,
        "request_timeout": 120,
    },
    tools=["user_input", "user_output"],
)

GROUP_CHAT_MANAGER = AgentConfig(
    role=AgentRole.GROUP_MANAGER,
    name="GroupChatManager",
    description="Manages and coordinates conversations between multiple agents, ensuring proper flow of information.",
    llm_config={
        "temperature": 0.7,
        "request_timeout": 120,
    },
    tools=["message_routing", "conversation_management"],
)

# Specialized agents
BOOKING_AGENT = AgentConfig(
    role=AgentRole.BOOKING,
    name="BookingAgent",
    description="Handles all types of reservations including rooms, restaurants, events, and services.",
    llm_config={
        "temperature": 0.3,  # Lower temperature for more precise booking handling
        "request_timeout": 60,
    },
    tools=[
        "room_booking",
        "restaurant_booking",
        "event_booking",
        "service_appointment",
    ],
)

CUSTOMER_SERVICE_AGENT = AgentConfig(
    role=AgentRole.CUSTOMER_SERVICE,
    name="CustomerServiceAgent",
    description="Manages customer inquiries, feedback, and FAQ responses.",
    llm_config={
        "temperature": 0.7,  # Higher temperature for more natural conversation
        "request_timeout": 60,
    },
    tools=[
        "customer_info",
        "feedback_management",
        "faq_lookup",
    ],
)

FACILITIES_AGENT = AgentConfig(
    role=AgentRole.FACILITIES,
    name="FacilitiesAgent",
    description="Manages room and facility availability, amenity access, and space allocation.",
    llm_config={
        "temperature": 0.3,
        "request_timeout": 60,
    },
    tools=[
        "room_management",
        "amenity_management",
        "space_management",
    ],
)

CONCIERGE_AGENT = AgentConfig(
    role=AgentRole.CONCIERGE,
    name="ConciergeAgent",
    description="Provides personalized recommendations and handles special requests.",
    llm_config={
        "temperature": 0.7,
        "request_timeout": 60,
    },
    tools=[
        "recommendation_lookup",
        "service_lookup",
        "promotion_lookup",
    ],
)

STAFF_COORDINATOR_AGENT = AgentConfig(
    role=AgentRole.STAFF_COORDINATOR,
    name="StaffCoordinatorAgent",
    description="Manages staff assignments, scheduling, and coordination.",
    llm_config={
        "temperature": 0.3,
        "request_timeout": 60,
    },
    tools=[
        "staff_management",
        "schedule_management",
        "event_tracking",
    ],
)

ANALYTICS_AGENT = AgentConfig(
    role=AgentRole.ANALYTICS,
    name="AnalyticsAgent",
    description="Monitors system performance, analyzes usage patterns, and tracks financial transactions.",
    llm_config={
        "temperature": 0.3,
        "request_timeout": 90,
    },
    tools=[
        "usage_analytics",
        "payment_tracking",
        "performance_monitoring",
    ],
)

ORCHESTRATOR_AGENT = AgentConfig(
    role=AgentRole.ORCHESTRATOR,
    name="OrchestratorAgent",
    description="Coordinates between all other agents and manages overall workflow.",
    llm_config={
        "temperature": 0.5,
        "request_timeout": 90,
    },
    tools=[
        "task_routing",
        "workflow_management",
        "agent_coordination",
    ],
)

# Agent groupings for different scenarios
BOOKING_GROUP = [BOOKING_AGENT] * 3  # 3 booking agents for load handling
CUSTOMER_SERVICE_GROUP = [CUSTOMER_SERVICE_AGENT] * 2  # 2 customer service agents
CORE_GROUP = [
    FACILITIES_AGENT,
    CONCIERGE_AGENT,
    STAFF_COORDINATOR_AGENT,
    ANALYTICS_AGENT,
]

# Complete agent system configuration
AGENT_SYSTEM_CONFIG = {
    "user_proxy": USER_PROXY,
    "group_manager": GROUP_CHAT_MANAGER,
    "booking_agents": BOOKING_GROUP,
    "customer_service_agents": CUSTOMER_SERVICE_GROUP,
    "core_agents": CORE_GROUP,
    "orchestrator": ORCHESTRATOR_AGENT,
}
