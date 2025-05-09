"""Script to check Neon.tech database connection and create tables."""

import os
import asyncio
import asyncpg
from dotenv import load_dotenv


async def main():
    """Check database connection and create tables."""
    # Load environment variables
    load_dotenv()

    print("Connecting to database...")
    conn = await asyncpg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )

    try:
        # Check if vector extension is available
        print("\nChecking vector extension...")
        result = await conn.fetchval(
            "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')"
        )
        if result:
            print("✓ Vector extension is enabled")
        else:
            print("Creating vector extension...")
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")

        # Create tables
        print("\nCreating tables...")
        await conn.execute(
            """
        CREATE TABLE IF NOT EXISTS faqs (
            id SERIAL PRIMARY KEY,
            question TEXT NOT NULL UNIQUE,
            answer TEXT NOT NULL,
            embedding vector(1536),
            category TEXT,
            subcategory TEXT,
            keywords TEXT[],
            helpful_votes INTEGER DEFAULT 0,
            views INTEGER DEFAULT 0,
            last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
        """
        )
        print("✓ Created faqs table")

        await conn.execute(
            """
        CREATE TABLE IF NOT EXISTS recommendations (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL,
            embedding vector(1536),
            category TEXT NOT NULL,
            price_range TEXT,
            rating FLOAT,
            distance_km FLOAT,
            tags TEXT[],
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
        """
        )
        print("✓ Created recommendations table")

        # Create indexes
        print("\nCreating indexes...")
        await conn.execute(
            """
        CREATE INDEX IF NOT EXISTS faqs_embedding_idx 
        ON faqs USING ivfflat (embedding vector_cosine_ops)
        """
        )
        print("✓ Created faqs index")

        await conn.execute(
            """
        CREATE INDEX IF NOT EXISTS recommendations_embedding_idx 
        ON recommendations USING ivfflat (embedding vector_cosine_ops)
        """
        )
        print("✓ Created recommendations index")

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

        print("\nSetup completed successfully!")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
