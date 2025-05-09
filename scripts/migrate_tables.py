"""Script to migrate data from old tables to new ones."""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_db_connection():
    """Get database connection."""
    return create_engine(
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )


def migrate_faqs(conn):
    """Migrate data from faq_knowledge_base to faqs."""
    print("Migrating FAQs...")

    # Copy data from old table to new table
    conn.execute(
        text(
            """
        INSERT INTO faqs (
            question, answer, embedding, category, subcategory,
            keywords, helpful_votes
        )
        SELECT 
            question, answer, 
            embedding::vector(1536),
            category, subcategory,
            keywords, helpful_votes
        FROM faq_knowledge_base
        ON CONFLICT (question) DO NOTHING
    """
        )
    )

    print("FAQs migration completed")


def migrate_recommendations(conn):
    """Migrate data from recommendations_knowledge_base to recommendations."""
    print("Migrating recommendations...")

    # Copy data from old table to new table
    conn.execute(
        text(
            """
        INSERT INTO recommendations (
            name, description, embedding, category,
            price_range, rating, distance_km, tags
        )
        SELECT 
            name, description,
            embedding::vector(1536),
            category, price_range, rating,
            distance_km, tags
        FROM recommendations_knowledge_base
        ON CONFLICT (name) DO NOTHING
    """
        )
    )

    print("Recommendations migration completed")


def main():
    """Run the migration."""
    try:
        engine = get_db_connection()
        with engine.connect() as conn:
            # Start transaction
            with conn.begin():
                # Check if old tables exist
                old_tables = conn.execute(
                    text(
                        """
                    SELECT tablename FROM pg_tables 
                    WHERE schemaname = 'public' 
                    AND tablename IN ('faq_knowledge_base', 'recommendations_knowledge_base')
                """
                    )
                ).fetchall()

                if not old_tables:
                    print("Old tables not found. Nothing to migrate.")
                    return

                # Migrate data
                migrate_faqs(conn)
                migrate_recommendations(conn)

                print("\nVerifying migration...")
                # Get counts
                faq_count = conn.execute(text("SELECT COUNT(*) FROM faqs")).scalar()
                rec_count = conn.execute(
                    text("SELECT COUNT(*) FROM recommendations")
                ).scalar()

                print(f"FAQs: {faq_count} rows")
                print(f"Recommendations: {rec_count} rows")

                print("\nMigration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {str(e)}")
        raise


if __name__ == "__main__":
    main()
