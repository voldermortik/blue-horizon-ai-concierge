"""Comprehensive demonstration of NLQueryService capabilities with production-ready features.

This demo showcases:
1. Basic and complex hotel queries
2. Real-world business scenarios
3. Analytical reporting queries
4. Rate limit handling with exponential backoff
5. Context handling and error recovery
6. Production-ready logging and cleanup
"""

import os
import logging
import time
from datetime import datetime, timedelta
from blue_horizon.services.nl_query_service import NLQueryService
from blue_horizon.models.openai_service import OpenAIService, OpenAIModel, RequestPriority
from blue_horizon.database.database import HotelDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def process_query_with_retry(
    service: NLQueryService,
    query: str,
    context: dict = None,
    max_retries: int = 2,
    base_delay: int = 20
) -> None:
    """Process a query with retry logic for rate limits.
    
    Args:
        service: NLQueryService instance
        query: Natural language query to process
        context: Optional context dictionary with user/session info
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
    """
    for attempt in range(max_retries + 1):
        try:
            logger.info(f"\nProcessing query: {query}")
            if context:
                logger.info(f"Context: {context}")
                
            result = service.process_query(query, context=context)
            
            # Log results
            logger.info(f"Intent: {result.intent}")
            logger.info(f"Category: {result.category}")
            logger.info(f"Entities: {result.entities}")
            if result.sql_query:
                logger.info(f"Generated SQL: {result.sql_query}")
            if result.response:
                logger.info(f"Response: {result.response}")
            if result.followup_questions:
                logger.info("Follow-up questions:")
                for q in result.followup_questions:
                    logger.info(f"- {q}")
            return result
            
        except Exception as e:
            if "429" in str(e) and attempt < max_retries:
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Rate limit hit. Waiting {delay} seconds before retry...")
                time.sleep(delay)
                continue
            logger.error(f"Error processing query: {e}")
            break

def test_basic_queries(service: NLQueryService):
    """Test basic hotel queries."""
    logger.info("\n=== Testing Basic Queries ===")
    
    # Room information query
    query = "What deluxe rooms are available next week with ocean view?"
    process_query_with_retry(service, query)
    time.sleep(20)
    
    # Service booking query
    query = "I need to book a couples massage for tomorrow afternoon, preferably around 2 PM"
    process_query_with_retry(service, query)
    time.sleep(20)
    
    # Query with customer context
    context = {
        'customer_id': 'CUST123',
        'loyalty_tier': 'Gold',
        'previous_stays': 5
    }
    query = "What special offers are available for my tier?"
    process_query_with_retry(service, query, context=context)

def test_complex_queries(service: NLQueryService):
    """Test complex business scenarios."""
    logger.info("\n=== Testing Complex Queries ===")
    
    # Multi-intent booking query
    query = "I want to book a deluxe room for next weekend and also reserve a table at your best restaurant for Saturday night for 4 people"
    process_query_with_retry(service, query)
    time.sleep(20)
    
    # Staff scheduling query
    query = "Which spa therapists are available for deep tissue massages tomorrow between 2 PM and 6 PM?"
    process_query_with_retry(service, query)
    time.sleep(20)
    
    # Feedback analysis query
    query = "Show me customer feedback about our restaurant service from the last month with ratings above 4 stars"
    process_query_with_retry(service, query)
    time.sleep(20)
    
    # Event booking query
    query = "What's the status of all wedding bookings in the Grand Ballroom next month with more than 100 guests?"
    process_query_with_retry(service, query)
    time.sleep(20)
    
    # Complex availability query
    query = "Find available event spaces that can host a corporate conference next week for 200 people with catering and AV equipment"
    process_query_with_retry(service, query)

def test_analytical_queries(service: NLQueryService):
    """Test analytical and reporting queries."""
    logger.info("\n=== Testing Analytical Queries ===")
    
    # Revenue analysis
    query = "What was our total revenue from room bookings last month, broken down by room type?"
    process_query_with_retry(service, query)
    time.sleep(20)
    
    # Occupancy analysis
    query = "Show me the occupancy rate for each room type over the past 3 months"
    process_query_with_retry(service, query)
    time.sleep(20)
    
    # Service popularity
    query = "Which spa services were most popular among Gold tier members this year?"
    process_query_with_retry(service, query)

def main():
    """Run comprehensive tests of NLQueryService."""
    try:
        # Initialize services
        openai_service = OpenAIService(
            model=OpenAIModel.GPT4,
            temperature=0.1,
            priority=RequestPriority.HIGH
        )
        db = HotelDatabase()
        service = NLQueryService(openai_service, db)
        
        # Run test suites
        test_basic_queries(service)
        test_complex_queries(service)
        test_analytical_queries(service)
        
    except Exception as e:
        logger.error(f"Error in test script: {e}")
    finally:
        logger.info("\nCleaning up...")
        if 'service' in locals():
            service.cleanup()
        logger.info("Test script completed.")

if __name__ == "__main__":
    main() 