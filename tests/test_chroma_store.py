"""Tests for ChromaDB vector store implementation."""

import os
import shutil
from pathlib import Path
import pytest
from unittest.mock import patch, Mock, create_autospec
import httpx
from openai import AuthenticationError, RateLimitError
from chromadb.utils.embedding_functions import EmbeddingFunction

from llama_index.legacy.schema import Document
from blue_horizon.search.chroma_store import ChromaVectorStore


@pytest.fixture
def test_data():
    """Test data fixture."""
    return {
        "texts": [
            "What is machine learning?",
            "How does deep learning work?",
            "What are neural networks?",
        ],
        "metadata": [
            {"faq_id": "1", "category": "ML"},
            {"faq_id": "2", "category": "DL"},
            {"faq_id": "3", "category": "NN"},
        ],
    }


@pytest.fixture
def vector_store_dir(tmp_path):
    """Create a temporary directory for vector store."""
    test_dir = tmp_path / "test_vector_store"
    test_dir.mkdir()
    yield str(test_dir)
    # Cleanup
    shutil.rmtree(str(test_dir))


@pytest.fixture
def mock_openai_key():
    """Mock OpenAI API key."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
        yield


def test_initialization(vector_store_dir, mock_openai_key):
    """Test vector store initialization."""
    store = ChromaVectorStore(persist_dir=vector_store_dir)
    assert store.persist_dir == Path(vector_store_dir)
    assert store.client is not None
    assert store._collections == {}
    assert store.embedding_function is not None
    assert "SentenceTransformer" in str(type(store.embedding_function))


def test_fallback_on_missing_api_key(vector_store_dir):
    """Test fallback to SentenceTransformer when no API key is provided."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
        store = ChromaVectorStore(persist_dir=vector_store_dir)
        assert store.embedding_function is not None
        assert "SentenceTransformer" in str(type(store.embedding_function))


def test_fallback_on_rate_limit(vector_store_dir):
    """Test fallback to SentenceTransformer on OpenAI rate limit."""
    # Set up a valid-looking API key
    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-valid-looking-key"}):
        # Create a mock response for the rate limit error
        mock_response = Mock(spec=httpx.Response)
        mock_response.request = Mock(spec=httpx.Request)
        mock_response.status_code = 429
        mock_response.headers = {"x-request-id": "test-request-id"}

        # Create the store
        store = ChromaVectorStore(persist_dir=vector_store_dir)

        # Patch the OpenAI API to raise rate limit error
        with patch("openai.resources.embeddings.Embeddings.create") as mock_create:
            mock_create.side_effect = RateLimitError(
                message="Rate limit exceeded",
                response=mock_response,
                body={"error": {"message": "Rate limit exceeded"}},
            )

            # Create a collection to trigger embedding function setup
            collection = store.create_collection("test")

            try:
                # This should trigger retries and then fallback
                store._get_embeddings(["test text"])
            except Exception:
                pass

            # Verify the mock was called multiple times (retries)
            assert mock_create.call_count > 1

            # Verify we fell back to SentenceTransformer
            assert "SentenceTransformer" in str(type(store.embedding_function))


def test_create_collection(vector_store_dir, mock_openai_key):
    """Test collection creation and retrieval."""
    store = ChromaVectorStore(persist_dir=vector_store_dir)
    collection = store.create_collection("test_collection")
    assert collection is not None
    assert "test_collection" in store._collections

    # Test retrieving existing collection
    same_collection = store.create_collection("test_collection")
    assert same_collection == collection


def test_add_documents(vector_store_dir, test_data, mock_openai_key):
    """Test adding documents to a collection."""
    store = ChromaVectorStore(persist_dir=vector_store_dir)
    collection_name = "test_docs"

    documents = [
        Document(text=text, metadata=meta)
        for text, meta in zip(test_data["texts"], test_data["metadata"])
    ]

    doc_ids = store.add_documents(collection_name, documents, show_progress=False)
    assert len(doc_ids) == len(documents)
    assert store.count_documents(collection_name) == len(documents)


def test_search_basic(vector_store_dir, test_data, mock_openai_key):
    """Test basic search functionality."""
    store = ChromaVectorStore(persist_dir=vector_store_dir)
    collection_name = "test_search"

    documents = [
        Document(text=text, metadata=meta)
        for text, meta in zip(test_data["texts"], test_data["metadata"])
    ]

    store.add_documents(collection_name, documents, show_progress=False)
    results = store.search(collection_name, "machine learning", top_k=2)
    assert len(results) == 2
    assert all(isinstance(result["score"], float) for result in results)


def test_search_with_metadata_filter(vector_store_dir, test_data, mock_openai_key):
    """Test search with metadata filtering."""
    store = ChromaVectorStore(persist_dir=vector_store_dir)
    collection_name = "test_filter"

    documents = [
        Document(text=text, metadata=meta)
        for text, meta in zip(test_data["texts"], test_data["metadata"])
    ]

    store.add_documents(collection_name, documents, show_progress=False)

    filter_metadata = {"category": "ML"}
    results = store.search(
        collection_name, "machine learning", filter_metadata=filter_metadata
    )
    assert len(results) == 1
    assert results[0]["metadata"]["category"] == "ML"


def test_update_documents(vector_store_dir, test_data, mock_openai_key):
    """Test document updates."""
    store = ChromaVectorStore(persist_dir=vector_store_dir)
    collection_name = "test_update"

    # Add initial document with a specific ID
    doc_id = "test_doc_1"
    initial_doc = Document(
        text=test_data["texts"][0],
        metadata={"doc_id": doc_id, **test_data["metadata"][0]},
    )

    # Add document using the store's add_documents method to get the actual ID
    actual_ids = store.add_documents(
        collection_name, [initial_doc], show_progress=False
    )
    actual_id = actual_ids[0]

    # Get the collection and verify initial state
    collection = store.get_collection(collection_name)
    initial_docs = collection.get()
    assert len(initial_docs["documents"]) == 1

    # Delete using the actual ID
    collection.delete(ids=[actual_id])

    # Verify deletion
    after_delete = collection.get()
    assert len(after_delete.get("documents", [])) == 0

    # Add updated document using the same ID
    updated_doc = Document(
        text="Updated text content",
        metadata={"doc_id": doc_id, "category": "ML", "updated": True},
    )
    collection.add(
        ids=[actual_id], documents=[updated_doc.text], metadatas=[updated_doc.metadata]
    )

    # Verify update
    final_docs = collection.get()
    assert len(final_docs["documents"]) == 1
    assert "Updated text content" in final_docs["documents"][0]
    assert final_docs["metadatas"][0]["updated"] is True


def test_delete_documents(vector_store_dir, test_data, mock_openai_key):
    """Test document deletion."""
    store = ChromaVectorStore(persist_dir=vector_store_dir)
    collection_name = "test_delete"

    documents = [
        Document(text=text, metadata=meta)
        for text, meta in zip(test_data["texts"], test_data["metadata"])
    ]

    doc_ids = store.add_documents(collection_name, documents, show_progress=False)
    initial_count = store.count_documents(collection_name)

    store.delete_documents(collection_name, [doc_ids[0]])
    assert store.count_documents(collection_name) == initial_count - 1


def test_persistence(vector_store_dir, test_data, mock_openai_key):
    """Test that data persists between store instances."""
    # Create first store instance and add documents
    store1 = ChromaVectorStore(persist_dir=vector_store_dir)
    collection_name = "test_persist"

    documents = [
        Document(text=text, metadata=meta)
        for text, meta in zip(test_data["texts"], test_data["metadata"])
    ]

    store1.add_documents(collection_name, documents, show_progress=False)

    # Create new store instance with same persist_dir
    store2 = ChromaVectorStore(persist_dir=vector_store_dir)

    # Verify documents are still accessible
    assert store2.count_documents(collection_name) == len(documents)
    results = store2.search(collection_name, "machine learning")
    assert len(results) > 0
