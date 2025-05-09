"""Example script demonstrating the usage of NLQueryService."""

import os
from dotenv import load_dotenv

from blue_horizon.services.nl_query_service import NLQueryService
from blue_horizon.models.openai_service import (
    OpenAIService,
    OpenAIModel,
    RequestPriority,
)
from blue_horizon.database.database import HotelDatabase
from blue_horizon.utils.logger import log, LogLevel


def process_and_display_query(
    service: NLQueryService, query: str, context: dict = None, use_llm: bool = True
):
    """Process a query and display the results."""
    log(f"\nProcessing query: {query}", LogLevel.ON)

    try:
        # Process the query
        log("Attempting to process query...", LogLevel.VERBOSE)
        result = service.process_query(query, use_llm=use_llm, context=context)

        # Display results
        log(f"Intent: {result.intent.name}", LogLevel.ON)
        log(f"Category: {result.category}", LogLevel.ON)
        log(f"Priority: {result.priority.name}", LogLevel.ON)

        if result.entities:
            log("Entities found:", LogLevel.ON)
            for key, value in result.entities.items():
                log(f"  - {key}: {value}", LogLevel.ON)

        if result.requires_followup:
            log("Follow-up questions needed:", LogLevel.ON)
            for question in result.followup_questions:
                log(f"  - {question}", LogLevel.ON)

        if result.sql_query:
            log(f"Generated SQL query: {result.sql_query}", LogLevel.ON)

        if result.llm_response:
            log(f"LLM response: {result.llm_response}", LogLevel.ON)

        if result.token_usage:
            log(f"Token usage: {result.token_usage}", LogLevel.VERBOSE)

        return result

    except Exception as e:
        log(f"Error processing query: {str(e)}", LogLevel.ON)
        return None


def demonstrate_caching(service: NLQueryService):
    """Demonstrate the caching functionality."""
    log("\n=== Testing Query Caching ===", LogLevel.ON)

    # Process the same query twice to demonstrate caching
    query = "What are your room rates?"

    log("First attempt - should hit the API:", LogLevel.ON)
    result1 = process_and_display_query(service, query)

    log("\nSecond attempt - should use cache:", LogLevel.ON)
    result2 = process_and_display_query(service, query)

    # Show that results are identical
    if result1 and result2:
        log("Cache test successful - received identical responses", LogLevel.ON)


def demonstrate_error_handling(service: NLQueryService):
    """Demonstrate error handling capabilities."""
    log("\n=== Testing Error Handling ===", LogLevel.ON)

    # Test SQL injection attempt
    log("Testing SQL injection prevention:", LogLevel.ON)
    malicious_query = "Show me rooms; DROP TABLE bookings;"
    process_and_display_query(service, malicious_query)

    # Test empty query
    log("\nTesting empty query handling:", LogLevel.ON)
    process_and_display_query(service, "")

    # Test invalid query
    log("\nTesting invalid query handling:", LogLevel.ON)
    process_and_display_query(service, "!@#$%^")


def demonstrate_context_handling(service: NLQueryService):
    """Demonstrate context-aware query processing."""
    log("\n=== Testing Context-Aware Processing ===", LogLevel.ON)

    # Process queries with different contexts
    contexts = [
        {
            "customer_id": "CUST123",
            "loyalty_tier": "Gold",
            "previous_stays": 5,
            "preferences": {"room_type": "suite", "view": "ocean"},
        },
        {
            "customer_id": "CUST456",
            "loyalty_tier": "Silver",
            "previous_stays": 2,
            "preferences": {"room_type": "standard", "view": "city"},
        },
    ]

    query = "What rooms would you recommend for me?"

    for context in contexts:
        log(f"\nProcessing with context: {context}", LogLevel.ON)
        process_and_display_query(service, query, context)


def main():
    """Run example queries using NLQueryService."""
    try:
        # Load environment variables
        load_dotenv(override=True)

        # Initialize services
        log("Initializing services...", LogLevel.ON)
        openai_service = OpenAIService(
            model=OpenAIModel.GPT4, temperature=0.1, priority=RequestPriority.HIGH
        )
        db = HotelDatabase()
        service = NLQueryService(openai_service, db)

        # Demonstrate basic queries
        log("\n=== Testing Basic Queries ===", LogLevel.ON)

        # Example 1: Room Information Query
        query = "What deluxe rooms are available next week with ocean view?"
        process_and_display_query(service, query)

        # Example 2: Service Booking Query with Context
        context = {
            "customer_id": "CUST123",
            "loyalty_tier": "Gold",
            "previous_stays": 5,
        }
        query = "I need to book a couples massage for tomorrow afternoon, preferably around 2 PM"
        process_and_display_query(service, query, context)

        # Example 3: Restaurant Query
        query = "Do you have any restaurants that serve gluten-free food?"
        process_and_display_query(service, query)

        # Example 4: Complex Multi-Intent Query
        query = "I want to book a deluxe room for next weekend and also reserve a table at your best restaurant for Saturday night for 4 people"
        process_and_display_query(service, query)

        # Example 5: Special Request Query
        query = "I have a gluten allergy and need to know what accommodations you can provide"
        process_and_display_query(service, query)

        # Demonstrate additional features
        demonstrate_caching(service)
        demonstrate_error_handling(service)
        demonstrate_context_handling(service)

    except Exception as e:
        log(f"Error in main: {str(e)}", LogLevel.ON)
    finally:
        # Cleanup
        if "service" in locals():
            service.cleanup()
        log("Example script completed.", LogLevel.ON)


if __name__ == "__main__":
    main()
