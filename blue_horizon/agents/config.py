from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# OpenAI API configuration
OPENAI_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "model": "gpt-4-turbo-preview",  # Default model
    "temperature": 0.7,
    "max_tokens": 1000
}

# Agent configurations
CONCIERGE_MANAGER_CONFIG = {
    "name": "Concierge Manager",
    "description": "Main coordinator for the concierge service, delegates tasks to specialist agents",
    "instructions": """You are the head concierge manager at Blue Horizon Hotel. 
    Your role is to:
    1. Understand guest requests and coordinate with specialist agents
    2. Ensure high-quality service delivery
    3. Handle complex requests requiring multiple services
    4. Maintain context across conversations
    5. Know when to escalate to human staff""",
    "llm_config": OPENAI_CONFIG
}

SPECIALIST_CONFIGS = {
    "weather": {
        "name": "Weather Specialist",
        "description": "Handles weather-related inquiries and forecasts",
        "instructions": "You are a weather specialist who provides accurate weather information and forecasts.",
        "llm_config": OPENAI_CONFIG
    },
    "timezone": {
        "name": "Time Zone Specialist",
        "description": "Manages time zone conversions and scheduling",
        "instructions": "You are a timezone specialist who helps with time conversions and scheduling across time zones.",
        "llm_config": OPENAI_CONFIG
    },
    "restaurant": {
        "name": "Restaurant Specialist",
        "description": "Handles restaurant recommendations and reservations",
        "instructions": "You are a restaurant specialist who helps with dining recommendations and reservations.",
        "llm_config": OPENAI_CONFIG
    },
    "attractions": {
        "name": "Attractions Specialist",
        "description": "Manages local attraction information and bookings",
        "instructions": "You are an attractions specialist who provides information about local points of interest.",
        "llm_config": OPENAI_CONFIG
    },
    "transportation": {
        "name": "Transportation Specialist",
        "description": "Handles transportation arrangements",
        "instructions": "You are a transportation specialist who helps with travel arrangements and bookings.",
        "llm_config": OPENAI_CONFIG
    },
    "room_service": {
        "name": "Room Service Specialist",
        "description": "Manages room service orders and special requests",
        "instructions": "You are a room service specialist who handles in-room dining and special requests.",
        "llm_config": OPENAI_CONFIG
    }
}

CRITIC_CONFIG = {
    "name": "Service Critic",
    "description": "Validates and reviews service recommendations",
    "instructions": """You are a service quality critic who ensures:
    1. Recommendations are appropriate and feasible
    2. Schedules don't conflict
    3. Guest preferences are properly considered
    4. Service standards are maintained""",
    "llm_config": OPENAI_CONFIG
}

HUMAN_HANDOFF_CONFIG = {
    "name": "Human Handoff Manager",
    "description": "Manages escalation to human staff",
    "instructions": """You manage the handoff process to human staff when:
    1. Requests exceed agent capabilities
    2. Special approval is needed
    3. Complex problem resolution is required
    4. Guest specifically requests human assistance""",
    "llm_config": OPENAI_CONFIG
}

# Conversation configurations
CONVERSATION_CONFIGS = {
    "max_consecutive_auto_reply": 10,
    "human_input_mode": "TERMINATE",  # Options: NEVER, TERMINATE, ALWAYS
    "system_message": "Blue Horizon AI Concierge System - Providing exceptional service"
} 