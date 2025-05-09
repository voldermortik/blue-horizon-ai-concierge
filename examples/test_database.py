"""Test script for verifying database functionality."""

import os
from datetime import datetime, timedelta
from blue_horizon.database.database import HotelDatabase
from blue_horizon.utils.logger import log, LogLevel


def test_database_operations():
    """Test various database operations."""

    # Initialize database connection
    db_url = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

    try:
        log("Initializing database connection...", LogLevel.ON)
        db = HotelDatabase(db_url)

        # Reset database to ensure clean state
        log("\nResetting database to ensure clean state...", LogLevel.ON)
        db.reset_database()

        # Test room information retrieval
        log("\nTesting room information retrieval...", LogLevel.ON)
        rooms = db.get_room_info(room_type="deluxe")
        log(f"Found {len(rooms)} deluxe rooms", LogLevel.ON)

        # Test customer information retrieval
        log("\nTesting customer information retrieval...", LogLevel.ON)
        customers = db.get_customer_info()
        log(f"Found {len(customers)} customers", LogLevel.ON)

        # Test booking information retrieval
        log("\nTesting booking information retrieval...", LogLevel.ON)
        bookings = db.get_booking_info()
        log(f"Found {len(bookings)} bookings", LogLevel.ON)

        # Test service information retrieval
        log("\nTesting service information retrieval...", LogLevel.ON)
        services = db.get_service_info(service_type="spa")
        log(f"Found {len(services)} spa services", LogLevel.ON)

        # Test staff information retrieval
        log("\nTesting staff information retrieval...", LogLevel.ON)
        staff = db.get_staff_info()
        log(f"Found {len(staff)} staff members", LogLevel.ON)

        # Test event space availability
        log("\nTesting event space availability...", LogLevel.ON)
        tomorrow = datetime.now() + timedelta(days=1)
        spaces = db.get_event_space_info(capacity=50, date=tomorrow)
        log(f"Found {len(spaces)} available event spaces for tomorrow", LogLevel.ON)

        # Test restaurant booking information
        log("\nTesting restaurant booking information...", LogLevel.ON)
        restaurant_bookings = db.get_restaurant_booking_info(date=tomorrow)
        log(
            f"Found {len(restaurant_bookings)} restaurant bookings for tomorrow",
            LogLevel.ON,
        )

        # Test amenity information
        log("\nTesting amenity information retrieval...", LogLevel.ON)
        amenities = db.get_amenity_info(category="pool")
        log(f"Found {len(amenities)} pool amenities", LogLevel.ON)

        # Test promotion information
        log("\nTesting promotion information retrieval...", LogLevel.ON)
        promotions = db.get_promotion_info(status="active")
        log(f"Found {len(promotions)} active promotions", LogLevel.ON)

        # Test FAQ information
        log("\nTesting FAQ information retrieval...", LogLevel.ON)
        faqs = db.get_faq_info(category="general")
        log(f"Found {len(faqs)} general FAQs", LogLevel.ON)

        log("\nAll database tests completed successfully!", LogLevel.ON)

    except Exception as e:
        log(f"Error during database testing: {str(e)}", LogLevel.ON)
        raise
    finally:
        if "db" in locals():
            db.cleanup()
            log("Database connection cleaned up", LogLevel.ON)


if __name__ == "__main__":
    test_database_operations()
