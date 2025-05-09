"""Script to check vector tables in Neon.tech database."""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv


def main():
    """Check vector tables in Neon.tech database."""
    # Load environment variables
    load_dotenv()

    # Create database URL
    db_url = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

    # Create engine
    engine = create_engine(db_url)

    # Check tables
    with engine.connect() as conn:
        print("\nFAQ Knowledge Base:")
        result = conn.execute(text("SELECT COUNT(*) FROM faq_knowledge_base"))
        print(f"- {result.scalar()} rows")

        print("\nRecommendations Knowledge Base:")
        result = conn.execute(
            text("SELECT COUNT(*) FROM recommendations_knowledge_base")
        )
        print(f"- {result.scalar()} rows")

        print("\nEmbeddings:")
        result = conn.execute(text("SELECT COUNT(*) FROM embeddings"))
        print(f"- {result.scalar()} rows")


if __name__ == "__main__":
    main()
