import os
import asyncio
import asyncpg
from sqlalchemy import create_engine
from dotenv import load_dotenv
from blue_horizon.services.nl2sql_service import NL2SQLService


async def test_amenities_query():
    # Load environment variables
    load_dotenv()

    # Create database URL for Neon.tech
    db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

    print("\nInitializing NL2SQLService with Neon.tech connection...")
    service = NL2SQLService(
        db_url=db_url,
        redis_host=os.getenv("REMOTE_REDIS_HOST"),
        redis_port=int(os.getenv("REMOTE_REDIS_PORT", "6379")),
        redis_password=os.getenv("REMOTE_REDIS_PASSWORD"),
    )

    # Test query for amenities
    query = "List all unique amenities with their names, locations, categories and prices. Use DISTINCT to avoid duplicates."

    print(f"\nExecuting query: {query}")
    result = await service.query(query)

    # Print the SQL query that was generated
    print("\nGenerated SQL query:")
    print(result["metadata"]["sql_query"])

    # Print the results in a formatted way
    print("\nResults:")
    if "raw_result" in result["metadata"]:
        print(f"{'Name':<30} {'Location':<25} {'Category':<20} {'Price':<10}")
        print("-" * 85)
        for item in result["metadata"]["raw_result"]:
            name = item.get("DISTINCT name", item.get("name", "N/A"))
            location = item.get("location", "N/A")
            category = item.get("category", "N/A")
            price = f"${item.get('price', 0):.2f}"
            print(f"{name:<30} {location:<25} {category:<20} {price:<10}")
        print(f"\nTotal amenities found: {len(result['metadata']['raw_result'])}")
    else:
        print(result["results"])


if __name__ == "__main__":
    asyncio.run(test_amenities_query())
