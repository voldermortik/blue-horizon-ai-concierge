"""Script to migrate data from local PostgreSQL to Neon.tech."""

import os
import asyncio
import asyncpg
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Tables to migrate in order of dependencies
TABLES_TO_MIGRATE = [
    # Base tables (no dependencies)
    "customers",
    "amenities",
    "rooms",
    "staff",
    "services",
    "event_spaces",
    "restaurants",
    "promotions",
    # First level dependencies
    "customer_preferences",
    "customer_history",
    "room_availability",
    "room_bookings",
    "restaurant_bookings",
    "event_bookings",
    "event_space_bookings",
    "staff_schedules",
    "service_appointments",
    # Second level dependencies
    "payments",
    "feedback",
    "maintenance",
    "amenity_usage",
    # Knowledge base and tracking
    "embeddings",
    "faqs",
    "faq_knowledge_base",
    "recommendations",
    "recommendations_knowledge_base",
    "event_tracking",
]


async def get_local_connection():
    """Get connection to local PostgreSQL database."""
    return await asyncpg.connect(
        host="localhost",
        port=5432,
        user=os.getenv("LOCAL_DB_USER", "postgres"),
        password=os.getenv("LOCAL_DB_PASSWORD", "postgres"),
        database=os.getenv("LOCAL_DB_NAME", "blue_horizon"),
    )


async def get_neon_connection():
    """Get connection to Neon database."""
    return await asyncpg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        database=os.getenv("DB_NAME", "blue_horizon"),
    )


async def migrate_table(table_name: str, local_conn, neon_conn):
    """Migrate a table from local PostgreSQL to Neon.tech.

    Args:
        table_name: Name of the table to migrate
        local_conn: Local database connection
        neon_conn: Neon database connection
    """
    print(f"\nMigrating {table_name}...")

    try:
        # Get table schema
        schema = await local_conn.fetch(
            """
            SELECT column_name, data_type, character_maximum_length, 
                   is_nullable, column_default, udt_name
            FROM information_schema.columns 
            WHERE table_name = $1
            ORDER BY ordinal_position
            """,
            table_name,
        )

        if not schema:
            print(f"Table {table_name} not found in local database!")
            return

        # Create sequences first
        for col in schema:
            if col["column_default"] and "nextval" in col["column_default"]:
                seq_name = col["column_default"].split("'")[1].split("::")[0]
                try:
                    await neon_conn.execute(f"CREATE SEQUENCE IF NOT EXISTS {seq_name}")
                except Exception as e:
                    print(f"Warning: Could not create sequence {seq_name}: {str(e)}")

        # Create table in Neon if it doesn't exist
        columns = []
        for col in schema:
            # Handle special data types
            if col["udt_name"] == "vector":
                col_type = "vector(1536)"
            elif col["data_type"].startswith("ARRAY"):
                # Extract the base type from udt_name (e.g., "_text" -> "text[]")
                base_type = (
                    col["udt_name"][1:]
                    if col["udt_name"].startswith("_")
                    else col["udt_name"]
                )
                col_type = f"{base_type}[]"
            else:
                col_type = col["data_type"]
                if col["character_maximum_length"]:
                    col_type = f"{col_type}({col['character_maximum_length']})"

            nullable = "NOT NULL" if col["is_nullable"] == "NO" else ""
            default = (
                f"DEFAULT {col['column_default']}" if col["column_default"] else ""
            )
            columns.append(
                f"{col['column_name']} {col_type} {nullable} {default}".strip()
            )

        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {','.join(columns)}
        )
        """
        await neon_conn.execute(create_table_sql)

        # Get data from local database
        data = await local_conn.fetch(f"SELECT * FROM {table_name}")
        if not data:
            print(f"No data found in {table_name}")
            return

        print(f"Found {len(data)} rows to migrate")

        # Migrate data in batches
        batch_size = 1000
        for i in tqdm(range(0, len(data), batch_size), desc=f"Migrating {table_name}"):
            batch = data[i : i + batch_size]

            # Generate placeholders for the INSERT statement
            placeholders = []
            values = []
            for row in batch:
                row_placeholders = []
                for j, val in enumerate(row, start=1):
                    values.append(val)
                    row_placeholders.append(f"${len(values)}")
                placeholders.append(f"({','.join(row_placeholders)})")

            # Insert batch into Neon
            columns_str = ",".join(col["column_name"] for col in schema)
            insert_sql = f"""
            INSERT INTO {table_name} ({columns_str})
            VALUES {','.join(placeholders)}
            ON CONFLICT DO NOTHING
            """
            await neon_conn.execute(insert_sql, *values)

        # Verify row count
        neon_count = await neon_conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
        print(f"Migrated {neon_count} rows to {table_name}")

    except Exception as e:
        print(f"Error migrating {table_name}: {str(e)}")
        raise


async def verify_migration(local_conn, neon_conn):
    """Verify that all tables were migrated successfully."""
    print("\nVerifying migration...")

    for table in TABLES_TO_MIGRATE:
        local_count = await local_conn.fetchval(f"SELECT COUNT(*) FROM {table}")
        neon_count = await neon_conn.fetchval(f"SELECT COUNT(*) FROM {table}")
        print(f"- {table}: {local_count} rows (local) -> {neon_count} rows (Neon)")


async def main():
    """Run the migration."""
    try:
        # Connect to databases
        print("Connecting to local PostgreSQL database...")
        local_conn = await get_local_connection()

        print("Connecting to Neon.tech database...")
        neon_conn = await get_neon_connection()

        # Enable vector extension in Neon
        print("Enabling vector extension in Neon.tech...")
        await neon_conn.execute("CREATE EXTENSION IF NOT EXISTS vector")

        # Migrate tables in order
        for table in TABLES_TO_MIGRATE:
            await migrate_table(table, local_conn, neon_conn)

        # Verify migration
        await verify_migration(local_conn, neon_conn)

        print("\nMigration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {str(e)}")
        raise
    finally:
        if "local_conn" in locals():
            await local_conn.close()
        if "neon_conn" in locals():
            await neon_conn.close()


if __name__ == "__main__":
    asyncio.run(main())
