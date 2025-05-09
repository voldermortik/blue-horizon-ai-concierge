"""Example script demonstrating how to query the migrated vector stores."""

from blue_horizon.search.chroma_store import ChromaVectorStore
from blue_horizon.utils.logger import log


def print_faq_results(results, query, section=""):
    """Print FAQ search results in a readable format."""
    print(f"\nSearch results for FAQ query{section}: '{query}'")
    print("-" * 80)
    for i, result in enumerate(results, 1):
        print(f"\nResult {i} (Score: {result['score']:.3f})")
        print(f"Category: {result['metadata']['category']}")
        print(f"Subcategory: {result['metadata']['subcategory']}")
        print(f"FAQ ID: {result['metadata']['faq_id']}")
        print(f"Helpful Votes: {result['metadata']['helpful_votes']}")
        print(f"Views: {result['metadata']['views']}")
        print(f"Text:\n{result['text']}")


def print_recommendation_results(results, query, section=""):
    """Print recommendation search results in a readable format."""
    print(f"\nSearch results for recommendation query{section}: '{query}'")
    print("-" * 80)
    for i, result in enumerate(results, 1):
        print(f"\nResult {i} (Score: {result['score']:.3f})")
        print(f"Name: {result['metadata']['name']}")
        print(f"Category: {result['metadata']['category']}")
        print(f"Rating: {result['metadata']['rating']}")
        print(f"Price Range: {result['metadata']['price_range']}")
        print(f"Distance: {result['metadata']['distance_km']}km")
        print(f"Tags: {result['metadata']['tags']}")
        print(f"Text:\n{result['text']}")


def main():
    """Run vector store queries."""
    # Initialize vector store with OpenAI embeddings
    store = ChromaVectorStore(
        persist_dir="vector_store",
        embedding_model="text-embedding-3-large",  # Use the latest large model
    )

    print("\n=== FAQ Queries ===")

    # 1. Basic semantic search
    print("\n1. Basic Semantic Search")
    queries = [
        "What is the cancellation policy?",
        "How can I book a room?",
        "Tell me about breakfast options",
    ]
    for query in queries:
        results = store.search("faqs", query, top_k=2)
        print_faq_results(results, query)

    # 2. Search with metadata filters
    print("\n2. Metadata-Filtered Searches")

    # Search in specific category
    query = "What services are available?"
    filter_metadata = {"category": "Services"}
    results = store.search("faqs", query, top_k=2, filter_metadata=filter_metadata)
    print_faq_results(results, query, " (filtered by Services category)")

    # Search for most viewed FAQs
    query = "hotel policies"
    filter_metadata = {"views": {"$gte": 100}}
    results = store.search("faqs", query, top_k=2, filter_metadata=filter_metadata)
    print_faq_results(results, query, " (filtered by most viewed)")

    print("\n=== Recommendation Queries ===")

    # 1. Basic recommendation search
    print("\n1. Basic Semantic Search")
    queries = [
        "I want a nice restaurant for dinner",
        "outdoor activities near the hotel",
        "cultural attractions to visit",
    ]
    for query in queries:
        results = store.search("recommendations", query, top_k=2)
        print_recommendation_results(results, query)

    # 2. Search with metadata filters
    print("\n2. Metadata-Filtered Searches")

    # High-rated places (rating >= 4.5)         
    query = "best places to eat"
    filter_metadata = {"rating": {"$gte": 4.5}}
    results = store.search(
        "recommendations", query, top_k=2, filter_metadata=filter_metadata
    )
    print_recommendation_results(results, query, " (high-rated places)")

    # Search for budget-friendly places nearby
    print(
        "\nSearch results for recommendation query (nearby budget-friendly places): 'places to visit'\n"
    )
    filter_metadata = {
        "$and": [{"distance_km": {"$lte": 2.0}}, {"price_range": {"$in": ["$", "$$"]}}]
    }
    results = store.search(
        "recommendations", "places to visit", top_k=2, filter_metadata=filter_metadata
    )
    print_recommendation_results(
        results, "places to visit", " (nearby budget-friendly)"
    )

    # Category-specific search
    query = "entertainment"
    filter_metadata = {"category": "Entertainment"}
    results = store.search(
        "recommendations", query, top_k=2, filter_metadata=filter_metadata
    )
    print_recommendation_results(results, query, " (entertainment category)")


if __name__ == "__main__":
    main()
