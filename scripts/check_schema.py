"""Script to check database schema."""

import asyncio
import asyncpg
from dotenv import load_dotenv
import os


async def main():
    """Check database schema."""
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
        # List all schemas
        print("\nAvailable schemas:")
        schemas = await conn.fetch(
            """
        SELECT schema_name 
        FROM information_schema.schemata
        """
        )
        for schema in schemas:
            print(f"- {schema['schema_name']}")

        # List all tables in public schema
        print("\nTables in public schema:")
        tables = await conn.fetch(
            """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        """
        )
        for table in tables:
            print(f"- {table['table_name']}")

            # Get table columns
            columns = await conn.fetch(
                """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = $1
            """,
                table["table_name"],
            )

            print("  Columns:")
            for col in columns:
                nullable = "NULL" if col["is_nullable"] == "YES" else "NOT NULL"
                print(f"  - {col['column_name']}: {col['data_type']} {nullable}")
            print()

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
