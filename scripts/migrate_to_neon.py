"""Script to migrate vector data from ChromaDB to Neon.tech."""

import os
from pathlib import Path
import asyncio
import asyncpg
from tqdm import tqdm
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings

# Load environment variables
load_dotenv(override=True)


async def get_neon_connection():
    """Get connection to Neon database."""
    return await asyncpg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        database=os.getenv("DB_NAME", "blue_horizon"),
    )


async def migrate_collection(collection_name: str, table_name: str, conn):
    """Migrate a ChromaDB collection to Neon.tech.

    Args:
        collection_name: Name of ChromaDB collection
        table_name: Name of target Neon.tech table
        conn: Database connection
    """
    print(f"\nMigrating {collection_name} to {table_name}...")

    # Initialize ChromaDB client
    client = chromadb.PersistentClient(
        path="vector_store",
        settings=Settings(
            anonymized_telemetry=False, allow_reset=True, is_persistent=True
        ),
    )
    collection = client.get_collection(name=collection_name)

    if not collection:
        print(f"Collection {collection_name} not found!")
        return

    # Get all documents with embeddings
    results = collection.get(include=["documents", "metadatas", "embeddings"])

    if not results or not results["ids"]:
        print(f"No documents found in {collection_name}!")
        return

    print(f"Found {len(results['ids'])} documents to migrate")

    # Prepare batch insert
    if table_name == "faq_knowledge_base":
        # Insert FAQs
        for i in tqdm(range(len(results["ids"])), desc=f"Migrating {collection_name}"):
            metadata = results["metadatas"][i]
            text = results["documents"][i]

            # Extract question and answer from text
            text_parts = text.split("\n")
            category = next(
                (
                    part.replace("Category: ", "")
                    for part in text_parts
                    if part.startswith("Category: ")
                ),
                "",
            )
            subcategory = next(
                (
                    part.replace("Subcategory: ", "")
                    for part in text_parts
                    if part.startswith("Subcategory: ")
                ),
                "",
            )
            question = next(
                (
                    part.replace("Question: ", "")
                    for part in text_parts
                    if part.startswith("Question: ")
                ),
                "",
            )
            answer = next(
                (
                    part.replace("Answer: ", "")
                    for part in text_parts
                    if part.startswith("Answer: ")
                ),
                "",
            )

            await conn.execute(
                """
                INSERT INTO faq_knowledge_base (
                    faq_id, category, subcategory, question, answer, keywords, 
                    last_updated, helpful_votes, views
                ) VALUES ($1, $2, $3, $4, $5, $6, NOW(), $7, $8)
                ON CONFLICT (faq_id) DO UPDATE SET
                    category = EXCLUDED.category,
                    subcategory = EXCLUDED.subcategory,
                    question = EXCLUDED.question,
                    answer = EXCLUDED.answer,
                    keywords = EXCLUDED.keywords,
                    last_updated = EXCLUDED.last_updated,
                    helpful_votes = EXCLUDED.helpful_votes,
                    views = EXCLUDED.views
                """,
                metadata.get("faq_id"),
                category,
                subcategory,
                question,
                answer,
                metadata.get("keywords"),
                int(metadata.get("helpful_votes", 0)),
                int(metadata.get("views", 0)),
            )

    elif table_name == "recommendations_knowledge_base":
        # Insert recommendations
        for i in tqdm(range(len(results["ids"])), desc=f"Migrating {collection_name}"):
            metadata = results["metadatas"][i]
            text = results["documents"][i]

            # Extract fields from text
            text_parts = text.split("\n")
            name = next(
                (
                    part.replace("Name: ", "")
                    for part in text_parts
                    if part.startswith("Name: ")
                ),
                "",
            )
            category = next(
                (
                    part.replace("Category: ", "")
                    for part in text_parts
                    if part.startswith("Category: ")
                ),
                "",
            )
            description = next(
                (
                    part.replace("Description: ", "")
                    for part in text_parts
                    if part.startswith("Description: ")
                ),
                "",
            )
            tags = next(
                (
                    part.replace("Tags: ", "")
                    for part in text_parts
                    if part.startswith("Tags: ")
                ),
                "",
            )
            price_range = next(
                (
                    part.replace("Price Range: ", "")
                    for part in text_parts
                    if part.startswith("Price Range: ")
                ),
                "",
            )

            # Generate a default address based on the name and category
            address = f"{name}, {category} District"

            await conn.execute(
                """
                INSERT INTO recommendations_knowledge_base (
                    recommendation_id, category, name, description, address, distance_km,
                    price_range, rating, review_count, tags, keywords, last_verified,
                    booking_required, seasonal
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW(), $12, $13)
                ON CONFLICT (recommendation_id) DO UPDATE SET
                    category = EXCLUDED.category,
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    address = EXCLUDED.address,
                    distance_km = EXCLUDED.distance_km,
                    price_range = EXCLUDED.price_range,
                    rating = EXCLUDED.rating,
                    review_count = EXCLUDED.review_count,
                    tags = EXCLUDED.tags,
                    keywords = EXCLUDED.keywords,
                    last_verified = EXCLUDED.last_verified,
                    booking_required = EXCLUDED.booking_required,
                    seasonal = EXCLUDED.seasonal
                """,
                metadata.get("recommendation_id"),
                category,
                name,
                description,
                address,
                float(metadata.get("distance_km", 0.0)),
                price_range,
                float(metadata.get("rating", 0.0)),
                int(metadata.get("review_count", 0)),
                tags,
                metadata.get("keywords"),
                bool(metadata.get("booking_required", False)),
                bool(metadata.get("seasonal", False)),
            )


async def verify_migration(conn):
    """Verify that data was migrated successfully."""
    faq_count = await conn.fetchval("SELECT COUNT(*) FROM faq_knowledge_base")
    rec_count = await conn.fetchval(
        "SELECT COUNT(*) FROM recommendations_knowledge_base"
    )

    print("\nMigration verification:")
    print(f"- FAQs migrated: {faq_count}")
    print(f"- Recommendations migrated: {rec_count}")


async def main():
    """Run the migration."""
    try:
        # Connect to Neon.tech
        print("Connecting to Neon.tech database...")
        conn = await get_neon_connection()

        # Migrate collections
        await migrate_collection("faqs", "faq_knowledge_base", conn)
        await migrate_collection(
            "recommendations", "recommendations_knowledge_base", conn
        )

        # Verify migration
        await verify_migration(conn)

        print("\nMigration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {str(e)}")
        raise
    finally:
        if "conn" in locals():
            await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
