"""Script to create necessary tables in Neon.tech database."""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def create_tables():
    """Create necessary tables in Neon.tech database."""
    try:
        print("Connecting to Neon.tech database...")
        conn = await asyncpg.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            database=os.getenv("DB_NAME", "blue_horizon"),
        )

        print("Enabling vector extension...")
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")

        print("Creating faq_knowledge_base table...")
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS public.faq_knowledge_base (
                faq_id VARCHAR PRIMARY KEY,
                category VARCHAR NOT NULL,
                subcategory VARCHAR,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                keywords TEXT,
                last_updated TIMESTAMP WITH TIME ZONE,
                helpful_votes INTEGER DEFAULT 0,
                views INTEGER DEFAULT 0
            )
        """
        )

        print("Dropping existing recommendations_knowledge_base table...")
        await conn.execute("DROP TABLE IF EXISTS public.recommendations_knowledge_base")

        print("Creating recommendations_knowledge_base table...")
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS public.recommendations_knowledge_base (
                recommendation_id VARCHAR PRIMARY KEY,
                category VARCHAR NOT NULL,
                name VARCHAR NOT NULL,
                description TEXT NOT NULL,
                address VARCHAR,
                distance_km FLOAT NOT NULL,
                price_range VARCHAR NOT NULL,
                rating FLOAT NOT NULL,
                review_count INTEGER NOT NULL,
                booking_required BOOLEAN DEFAULT FALSE,
                seasonal BOOLEAN DEFAULT FALSE,
                tags TEXT,
                keywords TEXT,
                last_verified TIMESTAMP WITH TIME ZONE
            )
        """
        )

        # Verify tables exist
        print("\nVerifying tables...")
        tables = await conn.fetch(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            """
        )
        print("Available tables:", [table["table_name"] for table in tables])

        print("Tables created successfully!")

    except Exception as e:
        print(f"Error creating tables: {str(e)}")
        raise
    finally:
        if "conn" in locals():
            await conn.close()


if __name__ == "__main__":
    asyncio.run(create_tables())
