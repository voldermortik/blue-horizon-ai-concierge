"""Example usage of the Blue Horizon AI Concierge package."""

from typing import Optional

from blue_horizon import (
    OpenAIModel,
    OpenAIService,
    SERVICE_DESCRIPTIONS,
    config,
    retry_with_backoff,
)


def generate_spa_description() -> Optional[str]:
    """Generate a service description for spa treatment with fallback handling.

    Returns:
        str: Generated description text, or None if generation fails
    """
    openai_service = OpenAIService(
        primary_model=OpenAIModel.GPT4,
        fallback_model=OpenAIModel.GPT35_TURBO,
    )

    description = openai_service.generate_service_description(
        service_type="Spa Treatment",
        static_fallbacks=SERVICE_DESCRIPTIONS,  # Fallback from prompts.py
    )
    return description


def main() -> None:
    """Run the example usage demonstration."""
    try:
        description = retry_with_backoff(
            generate_spa_description,
            max_retries=config.MAX_RETRIES,
        )
        print(f"Generated description: {description}")
    except Exception as e:
        print(f"Failed to generate description: {e}")


if __name__ == "__main__":
    main()
