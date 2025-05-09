import os
from pathlib import Path
import psycopg2
from dotenv import load_dotenv


def main():
    # Load environment variables
    load_dotenv()

    # Get database connection details from environment variables
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
        script_path = Path(__file__).parent / "update_room_availability.sql"
        with open(script_path, "r") as f:
            sql_script = f.read()

        print("Executing room availability update script...")
        # Execute the SQL script
        cur.execute(sql_script)

        print("Room availability update completed successfully!")

    except Exception as e:
        print(f"Error updating room availability: {str(e)}")
        raise
    finally:
        if "cur" in locals():
            cur.close()
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    main()
