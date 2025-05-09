import redis
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TestRedisError(Exception):
    """Exception raised for errors in the test_redis module."""


def test_redis_connection():
    """Test Redis connection and basic operations."""
    print("Testing Redis connection...")

    # Redis Cloud connection details
    redis_host = os.getenv("REMOTE_REDIS_HOST")
    redis_port = os.getenv("REMOTE_REDIS_PORT")
    redis_password = os.getenv("REMOTE_REDIS_PASSWORD")

    if not redis_password:
        raise ValueError("Redis password not found in .env file")

    print(f"Connecting to Redis at {redis_host}:{redis_port}")

    try:
        # Connect with minimal configuration
        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True,
        )

        # Test 1: Basic connection
        print("\n1. Testing connection...")
        result = r.ping()
        print(f"Connection test: {'✅ Passed' if result else '❌ Failed'}")

        # Test 2: Set and get
        print("\n2. Testing set/get operations...")
        test_key = "test:connection"
        test_value = f"Connection test at {datetime.now()}"
        r.set(test_key, test_value)
        retrieved = r.get(test_key)
        print(
            f"Set/Get test: {'✅ Passed' if retrieved == test_value else '❌ Failed'}"
        )
        print(f"Retrieved value: {retrieved}")

        # Test 3: Delete
        print("\n3. Testing delete operation...")
        r.delete(test_key)
        deleted_value = r.get(test_key)
        print(f"Delete test: {'✅ Passed' if deleted_value is None else '❌ Failed'}")

        print("\n✨ All tests completed successfully!")

    except redis.ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
    except TestRedisError as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    test_redis_connection()
