import os
from pathlib import Path
import psycopg2
from dotenv import load_dotenv


def main():
    # Load environment variables
    load_dotenv()

    # Get database connection details
    db_url = os.getenv("DB_URL")
    if not db_url:
        raise ValueError("DB_URL environment variable is not set")

    try:
        # Connect to the database
        print("Connecting to Neon.tech database...")
        conn = psycopg2.connect(db_url)
        conn.autocommit = True  # We want each statement to be committed immediately

        # Create a cursor
        cur = conn.cursor()

        # Read the SQL script
        script_path = Path(__file__).parent / "add_indexes.sql"
        with open(script_path, "r") as f:
            sql_script = f.read()

        print("Creating indexes...")
        # Execute each statement separately
        statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]
        for stmt in statements:
            print(f"Executing: {stmt[:100]}...")  # Print first 100 chars of statement
            cur.execute(stmt)

        print("Indexes created successfully!")

    except Exception as e:
        print(f"Error creating indexes: {str(e)}")
        raise
    finally:
        if "cur" in locals():
            cur.close()
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    main()
