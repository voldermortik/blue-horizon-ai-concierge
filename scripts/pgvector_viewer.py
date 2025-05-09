"""Streamlit-based viewer for pgvector store in Neon.tech."""

import os
from typing import List, Dict, Any
import json

import pandas as pd
import streamlit as st
import sqlalchemy as sa
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv(override=True)


def get_db_connection():
    """Create database connection."""
    db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    return create_engine(db_url)


def get_embedding(query: str, use_openai: bool = True) -> List[float]:
    """Get embedding for query text."""
    if use_openai:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.embeddings.create(
            model="text-embedding-3-small", input=query, encoding_format="float"
        )
        return response.data[0].embedding
    else:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        return model.encode(query).tolist()


def main():
    """Run the Streamlit-based pgvector store viewer application."""
    st.title("Vector Store Viewer (pgvector)")

    # Initialize database connection
    engine = get_db_connection()

    # Get available tables
    tables = ["faq_knowledge_base", "recommendations_knowledge_base", "embeddings"]
    selected_table = st.selectbox("Select Table", tables)

    if selected_table:
        try:
            # Display table info
            with engine.connect() as conn:
                # Get row count
                count = conn.execute(
                    text(f"SELECT COUNT(*) FROM {selected_table}")
                ).scalar()
                st.metric("Number of Records", count)

                # Display sample data
                query = f"SELECT * FROM {selected_table} LIMIT 5"
                df = pd.read_sql(query, conn)

                with st.expander("Sample Data"):
                    # Remove embedding column for display
                    display_df = (
                        df.drop("embedding", axis=1)
                        if "embedding" in df.columns
                        else df
                    )
                    st.dataframe(display_df)

            # Search functionality
            st.subheader("Vector Search")
            search_query = st.text_input("Enter search query")
            n_results = st.slider("Number of results", 1, 10, 5)
            use_openai = st.checkbox(
                "Use OpenAI for embeddings (uncheck to use SentenceTransformer)",
                value=True,
            )

            if search_query:
                with st.spinner("Generating embedding..."):
                    query_embedding = get_embedding(search_query, use_openai)

                # Perform vector search
                with engine.connect() as conn:
                    if selected_table == "faq_knowledge_base":
                        query = text(
                            """
                            SELECT question, answer, category, subcategory, 
                                   1 - (embedding <=> :embedding) as similarity
                            FROM faq_knowledge_base
                            ORDER BY embedding <=> :embedding
                            LIMIT :n
                        """
                        )
                    elif selected_table == "recommendations_knowledge_base":
                        query = text(
                            """
                            SELECT name, description, category, rating, price_range, 
                                   distance_km, tags, 1 - (embedding <=> :embedding) as similarity
                            FROM recommendations_knowledge_base
                            ORDER BY embedding <=> :embedding
                            LIMIT :n
                        """
                        )
                    else:  # embeddings table
                        query = text(
                            """
                            SELECT content, meta_data, 
                                   1 - (embedding <=> :embedding) as similarity
                            FROM embeddings
                            ORDER BY embedding <=> :embedding
                            LIMIT :n
                        """
                        )

                    results = conn.execute(
                        query, {"embedding": query_embedding, "n": n_results}
                    )

                    # Display results
                    st.subheader("Search Results")
                    for i, row in enumerate(results, 1):
                        similarity = row.similarity
                        with st.expander(f"Result {i} (Similarity: {similarity:.4f})"):
                            for col, val in row._mapping.items():
                                if col != "similarity":
                                    if isinstance(val, (dict, list)):
                                        st.json(val)
                                    else:
                                        st.write(f"**{col}:** {val}")

        except Exception as e:
            st.error(f"Error accessing table: {str(e)}")


if __name__ == "__main__":
    main()
