from typing import Dict, Any, Optional
from blue_horizon.agents.base_agent import BaseConciergAgent
from blue_horizon.agents.config import SPECIALIST_CONFIGS
from blue_horizon.tools.weather_tool import get_temperature

class WeatherAgent(BaseConciergAgent):
    """Specialist agent for handling weather-related inquiries"""
    
    def __init__(self):
        """Initialize the weather agent with its specific configuration"""
        config = SPECIALIST_CONFIGS["weather"]
        super().__init__(
            name=config["name"],
            description=config["description"],
            instructions=config["instructions"],
            llm_config=config["llm_config"]
        )
        
    def _extract_location(self, request: str) -> str:
        """Extract location from the request text.
        
        Args:
            request: The request text
            
        Returns:
            str: The extracted location
        """
        # Remove common weather-related words
        cleaned = request.lower()
        for word in ["weather", "temperature", "forecast", "in", "at", "for", "the"]:
            cleaned = cleaned.replace(word, "")
        
        # Clean up extra spaces and return
        return cleaned.strip()
        
    def handle_request(self, request: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Handle a weather-related request.
        
        Args:
            request: The incoming request text
            context: Optional context information
            
        Returns:
            str: Formatted weather information
        """
        try:
            # Extract location from request
            location = self._extract_location(request)
            if not location:
                return "I need a location to check the weather. Please specify a city."
            
            # Log the extracted location
            self.log_interaction(request, f"Extracted location: {location}", context)
            
            # Get weather data using our tool
            weather_data = get_temperature(location)
            
            # Check for errors
            if "error" in weather_data:
                error_msg = f"Sorry, I couldn't get the weather information: {weather_data['error']}"
                self.log_interaction(request, error_msg, {"error": weather_data['error']})
                return error_msg
            
            # Format the response
            response = self.format_weather_response(weather_data)
            
            # Log the interaction
            self.log_interaction(request, response, context)
            
            return response
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error while getting the weather information: {str(e)}"
            self.log_interaction(request, error_msg, {"error": str(e)})
            return error_msg
    
    def format_weather_response(self, weather_data: Dict[str, Any]) -> str:
        """Format weather data into a natural response.
        
        Args:
            weather_data: Dictionary containing weather information
            
        Returns:
            str: Formatted weather response
        """
        return f"""Current weather in {weather_data['location']}:
Temperature: {weather_data['temperature']}°C
Conditions: {weather_data['description']}"""
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the weather agent's capabilities.
        
        Returns:
            Dict[str, Any]: Dictionary of agent capabilities
        """
        return {
            "name": self.agent_name,
            "description": self.description,
            "can_handle": [
                "Current weather conditions",
                "Temperature information",
                "Weather descriptions"
            ]
        } 