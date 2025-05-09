"""Script to launch ChromaDB UI server for vector store visualization."""

import chromadb
from chromadb.config import Settings
import argparse


def main():
    parser = argparse.ArgumentParser(description="Launch ChromaDB UI server")
    parser.add_argument("--host", default="localhost", help="Host to run the server on")
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to run the server on"
    )
    parser.add_argument("--path", default="vector_store", help="Path to vector store")
    args = parser.parse_args()

    # Initialize ChromaDB client with UI enabled
    settings = Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=args.path,
        anonymized_telemetry=False,
        allow_reset=True,
        is_persistent=True,
    )

    # Create server instance
    server = chromadb.Server(host=args.host, port=args.port, settings=settings)

    print(f"\nLaunching ChromaDB UI server at http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop the server")

    # Run the server
    server.run()


if __name__ == "__main__":
    main()
