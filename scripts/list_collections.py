"""Script to list ChromaDB collections and their contents."""

import chromadb
from chromadb.config import Settings


def main():
    """List all collections in ChromaDB with details."""
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(
        path="vector_store",
        settings=Settings(
            anonymized_telemetry=False, allow_reset=True, is_persistent=True
        ),
    )

    # Get all collection names
    collection_names = client.list_collections()

    print("\nChromaDB Collections:")
    print("-" * 50)

    for name in collection_names:
        print(f"\nCollection: {name}")
        # Get the collection
        collection = client.get_collection(name=name)
        print(f"Number of documents: {collection.count()}")

        # Get a sample of documents
        try:
            results = collection.get(limit=1)
            if results and results["documents"]:
                print("\nSample document:")
                print(
                    "Text:",
                    (
                        results["documents"][0][:200] + "..."
                        if len(results["documents"][0]) > 200
                        else results["documents"][0]
                    ),
                )
                if results["metadatas"]:
                    print("Metadata:", results["metadatas"][0])
        except Exception as e:
            print(f"Error getting sample: {str(e)}")
        print("-" * 50)


if __name__ == "__main__":
    main()
