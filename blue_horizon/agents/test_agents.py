import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
logger.debug(f"Added {project_root} to Python path")

from blue_horizon.agents.weather_agent import WeatherAgent

async def test_weather_agent():
    """Test the weather agent's functionality"""
    
    # Load environment variables
    load_dotenv()
    logger.debug("Loaded environment variables")
    
    # Create weather agent
    logger.debug("Creating weather agent")
    weather_agent = WeatherAgent()
    logger.debug("Weather agent created")
    
    try:
        # Test basic weather request
        logger.info("\nTesting basic weather request:")
        response = await weather_agent._handle_message(
            "weather in London",
            sender=None,
            config={"context": {"test_type": "basic"}}
        )
        logger.info(f"Response: {response}")
        
        # Test empty location
        logger.info("\nTesting empty location:")
        response = await weather_agent._handle_message(
            "weather",
            sender=None,
            config={"context": {"test_type": "empty"}}
        )
        logger.info(f"Response: {response}")
        
        # Test invalid location
        logger.info("\nTesting invalid location:")
        response = await weather_agent._handle_message(
            "weather in InvalidCityXYZ",
            sender=None,
            config={"context": {"test_type": "invalid"}}
        )
        logger.info(f"Response: {response}")
        
        # Test capabilities
        logger.info("\nTesting agent capabilities:")
        capabilities = weather_agent.get_capabilities()
        logger.info(f"Capabilities: {capabilities}")
        
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}", exc_info=True)

if __name__ == "__main__":
    logger.debug("Starting test script")
    asyncio.run(test_weather_agent())
    logger.debug("Test script completed") 