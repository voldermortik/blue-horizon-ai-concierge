import os
from pathlib import Path
import psycopg2
from dotenv import load_dotenv
from tabulate import tabulate


def print_query_results(cursor, query, title):
    print(f"\n=== {title} ===")
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 1 and len(results[0]) == 1:
        print(results[0][0])
    else:
        headers = [desc[0] for desc in cursor.description]
        print(tabulate(results, headers=headers, tablefmt="psql"))
    print()


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

        # Create a cursor
        cur = conn.cursor()

        # Read the SQL script
        script_path = Path(__file__).parent / "check_room_data.sql"
        with open(script_path, "r") as f:
            queries = [q.strip() for q in f.read().split(";") if q.strip()]

        # Execute each query and print results
        titles = [
            "Total Room Count",
            "Room Types Distribution",
            "Total Room Availability Records",
            "Room Availability Status Distribution",
            "Price Range Information",
            "Room Occupancy Distribution",
        ]

        for query, title in zip(queries, titles):
            print_query_results(cur, query, title)

    except Exception as e:
        print(f"Error checking room data: {str(e)}")
        raise
    finally:
        if "cur" in locals():
            cur.close()
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    main()
