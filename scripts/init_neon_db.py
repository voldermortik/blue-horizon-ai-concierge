import os
import asyncio
import asyncpg
from dotenv import load_dotenv


async def init_database():
    """Initialize the Neon database with required extensions and tables."""
    try:
        # Load environment variables
        load_dotenv()

        # Get database connection parameters
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        dbname = os.getenv("DB_NAME", "blue_horizon")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "postgres")

        # Construct connection string
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

        print("Connecting to database...")
        conn = await asyncpg.connect(database_url)

        # Read and execute SQL script
        print("Reading SQL initialization script...")
        with open("scripts/init_neon_db.sql", "r", encoding="utf-8") as f:
            sql = f.read()

        print("Executing SQL initialization script...")
        await conn.execute(sql)

        print("Database initialization completed successfully!")

    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise
    finally:
        if "conn" in locals():
            await conn.close()


if __name__ == "__main__":
    asyncio.run(init_database())
