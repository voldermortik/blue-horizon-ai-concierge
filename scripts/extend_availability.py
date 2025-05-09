import os
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv
import psycopg2
from blue_horizon.data.generators.availability_generator import (
    generate_room_availability,
)


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

        # Get current room details
        print("Fetching room details...")
        room_details_df = pd.read_sql(
            """
            SELECT DISTINCT ON (r.room_id)
                r.room_id,
                r.room_number,
                r.max_occupancy,
                r.base_rate,
                r.max_rate,
                r.status
            FROM rooms r
        """,
            conn,
        )

        # Get existing bookings
        print("Fetching existing bookings...")
        bookings_df = pd.read_sql(
            """
            SELECT 
                room_number,
                check_in,
                check_out
            FROM room_bookings
            WHERE check_out > CURRENT_DATE
        """,
            conn,
        )

        # Get the latest date in room_availability
        latest_date = pd.read_sql(
            """
            SELECT MAX(date) as max_date 
            FROM room_availability
        """,
            conn,
        ).iloc[0]["max_date"]

        # Generate new availability data starting from the latest date
        print(f"Generating availability data from {latest_date}...")
        new_availability_df = generate_room_availability(
            room_details_df=room_details_df,
            bookings_df=bookings_df,
            start_date=latest_date,
            days_ahead=30,  # Extend by 30 days
        )

        # Insert new availability data
        print("Inserting new availability data...")
        new_availability_df.to_sql(
            "room_availability",
            conn,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000,
        )

        print("Room availability extension completed successfully!")

    except Exception as e:
        print(f"Error extending room availability: {str(e)}")
        raise
    finally:
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    main()
