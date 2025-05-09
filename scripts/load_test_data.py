"""Script to load test data into the vector store."""

import os
from datetime import datetime
from dotenv import load_dotenv

from blue_horizon.tools.search_tools import add_documents

# Load environment variables
load_dotenv(override=True)

# Sample policies
POLICIES = [
    {
        "content": """Check-in Policy:
        - Check-in time is 3:00 PM
        - Early check-in available upon request (subject to availability)
        - Valid ID and credit card required at check-in
        - Minimum age requirement: 21 years""",
        "metadata": {
            "type": "check-in",
            "last_updated": "2024-01-01",
        },
    },
    {
        "content": """Cancellation Policy:
        - Free cancellation up to 48 hours before check-in
        - Cancellations within 48 hours will incur one night's charge
        - No-shows will be charged for the entire stay
        - Special event dates may have different policies""",
        "metadata": {
            "type": "cancellation",
            "last_updated": "2024-01-01",
        },
    },
    {
        "content": """Pet Policy:
        - Dogs and cats welcome (max 2 pets per room)
        - Weight limit: 50 pounds per pet
        - $50 non-refundable pet fee per stay
        - Service animals exempt from fees
        - Pets must be leashed in public areas""",
        "metadata": {
            "type": "pet",
            "last_updated": "2024-01-01",
        },
    },
]

# Sample documentation
DOCUMENTATION = [
    {
        "content": """Blue Horizon Hotel Amenities:
        - 24-hour fitness center with modern equipment
        - Rooftop infinity pool with city views
        - Full-service spa offering massages and treatments
        - Business center with meeting rooms
        - Complimentary high-speed WiFi throughout""",
        "metadata": {
            "type": "amenities",
            "last_updated": "2024-01-01",
        },
    },
    {
        "content": """Room Types:
        - Deluxe King: 400 sq ft, city view, king bed
        - Ocean Suite: 800 sq ft, ocean view, separate living area
        - Executive Suite: 1000 sq ft, panoramic view, kitchenette
        - Penthouse: 2000 sq ft, private terrace, full kitchen""",
        "metadata": {
            "type": "rooms",
            "last_updated": "2024-01-01",
        },
    },
]


def main():
    """Load test data into vector store."""
    print("Loading test data into vector store...")

    # Load policies
    add_documents(
        collection_name="policies",
        documents=[p["content"] for p in POLICIES],
        metadatas=[p["metadata"] for p in POLICIES],
    )
    print("✓ Loaded policies")

    # Load documentation
    add_documents(
        collection_name="documentation",
        documents=[d["content"] for d in DOCUMENTATION],
        metadatas=[d["metadata"] for d in DOCUMENTATION],
    )
    print("✓ Loaded documentation")

    print("\nTest data loaded successfully!")


if __name__ == "__main__":
    main()
