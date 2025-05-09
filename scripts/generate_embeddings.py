"""Script to generate embeddings for FAQ and recommendation content."""

import os
import json
from typing import List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# Force reload environment variables
load_dotenv(override=True)


def get_embedding_with_transformer(
    model: SentenceTransformer, text: str
) -> List[float]:
    """Get embedding using SentenceTransformer model.

    Args:
        model: SentenceTransformer model
        text: Text to get embedding for

    Returns:
        List of floats representing the embedding
    """
    embedding = model.encode(text)
    return embedding.tolist()


def get_embedding(client: OpenAI, content: str, model: str) -> List[float]:
    """Get embedding for text using OpenAI API with fallback to SentenceTransformer.

    Args:
        client: OpenAI client
        content: Text to get embedding for
        model: OpenAI model to use

    Returns:
        List of floats representing the embedding
    """
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small", input=content, encoding_format="float"
        )
        return response.data[0].embedding
    except Exception as e:
        print(
            f"\nFalling back to SentenceTransformer due to OpenAI API error: {str(e)}"
        )
        transformer_model = SentenceTransformer("all-MiniLM-L6-v2")
        return get_embedding_with_transformer(transformer_model, content)


def store_embedding(
    conn: Session,
    content: str,
    embedding: List[float],
    meta_data: Dict[str, Any] = None,
) -> None:
    """Store embedding in the database."""
    # Convert embedding list to PostgreSQL vector format
    vector_str = f"[{','.join(str(x) for x in embedding)}]"

    # Convert meta_data to JSON string
    meta_data_json = json.dumps(meta_data) if meta_data else None

    # Insert into database
    conn.execute(
        text(
            """
        WITH input_data AS (
            SELECT 
                :content AS content,
                cast(:embedding AS vector(1536)) AS embedding,
                cast(:meta_data AS jsonb) AS meta_data
        )
        INSERT INTO embeddings (content, embedding, meta_data)
        SELECT content, embedding, meta_data FROM input_data
    """
        ),
        {"content": content, "embedding": vector_str, "meta_data": meta_data_json},
    )
    conn.commit()


def main():
    """Generate and store embeddings."""
    # Load environment variables
    load_dotenv()

    # Initialize OpenAI client with API key
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("OPENAI_MODEL", "text-embedding-3-small")

    print(f"\nUsing OpenAI model: {model}")

    # Create database connection
    db_url = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    engine = create_engine(db_url)

    with engine.connect() as conn:
        # Process FAQs
        print("\nProcessing FAQs...")
        faqs = conn.execute(
            text(
                """
                SELECT faq_id, question, answer, category, subcategory
                FROM faq_knowledge_base
                """
            )
        ).fetchall()

        for faq in tqdm(faqs, desc="Generating FAQ embeddings"):
            # Combine question and answer for embedding
            content = f"Question: {faq.question}\nAnswer: {faq.answer}"
            embedding = get_embedding(client, content, model)

            # Store embedding with metadata
            store_embedding(
                conn,
                content,
                embedding,
                {
                    "type": "faq",
                    "faq_id": faq.faq_id,
                    "category": faq.category,
                    "subcategory": faq.subcategory,
                },
            )

        # Process recommendations
        print("\nProcessing recommendations...")
        recommendations = conn.execute(
            text(
                """
                SELECT recommendation_id, name, description, category,
                       price_range, rating, distance_km
                FROM recommendations_knowledge_base
                """
            )
        ).fetchall()

        for rec in tqdm(recommendations, desc="Generating recommendation embeddings"):
            # Combine name and description for embedding
            content = f"{rec.name}\n{rec.description}"
            embedding = get_embedding(client, content, model)

            # Store embedding with metadata
            store_embedding(
                conn,
                content,
                embedding,
                {
                    "type": "recommendation",
                    "recommendation_id": rec.recommendation_id,
                    "category": rec.category,
                    "price_range": rec.price_range,
                    "rating": rec.rating,
                    "distance_km": rec.distance_km,
                },
            )

        # Commit all changes
        conn.execute(text("COMMIT"))

    print("\nEmbedding generation completed!")


if __name__ == "__main__":
    main()
