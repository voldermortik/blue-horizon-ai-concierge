"""Tests for vector search functionality."""

import pytest
import os
import shutil
from typing import List, Dict, Any

from blue_horizon.search.vector_search import UnifiedSearch, BatchUpdateResult


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


def test_batch_update(vector_store_dir, test_data):
    """Test batch update functionality."""
    # Initialize search
    search = UnifiedSearch(
        persist_dir=vector_store_dir,
        max_batch_size=2,  # Small batch size for testing
        max_workers=2,
    )

    # Create initial index
    search.create_index(
        texts=test_data["texts"][:2],
        collection_name="test_collection",
        metadata=test_data["metadata"][:2],
    )

    # Prepare update data
    update_texts = [
        "What are transformers?",
        "How does reinforcement learning work?",
    ]
    update_metadata = [
        {"faq_id": "4", "category": "NLP"},
        {"faq_id": "5", "category": "RL"},
    ]

    # Perform batch update
    result = search.batch_update(
        collection_name="test_collection",
        texts=update_texts,
        metadata=update_metadata,
    )

    # Verify results
    assert isinstance(result, BatchUpdateResult)
    assert result.total_processed == 2
    assert len(result.successful_ids) == 2
    assert len(result.failed_ids) == 0
    assert result.success_rate == 1.0

    # Verify search results include new documents
    index = search.load_index("test_collection")
    results = search.search("transformers", index, top_k=1)
    assert len(results) == 1
    assert "transformers" in results[0]["text"].lower()


def test_batch_update_with_errors(vector_store_dir, test_data):
    """Test batch update with some expected failures."""
    search = UnifiedSearch(
        persist_dir=vector_store_dir,
        max_batch_size=2,
    )

    # Create initial index
    search.create_index(
        texts=test_data["texts"][:2],
        collection_name="test_collection",
        metadata=test_data["metadata"][:2],
    )

    # Prepare update data with some invalid entries
    update_texts = [
        "Valid text",
        "",  # Empty text should fail
        None,  # None should fail
    ]
    update_metadata = [
        {"faq_id": "4", "category": "TEST"},
        {"faq_id": "5", "category": "TEST"},
        {"faq_id": "6", "category": "TEST"},
    ]

    # Perform batch update
    result = search.batch_update(
        collection_name="test_collection",
        texts=update_texts,
        metadata=update_metadata,
    )

    # Verify results
    assert result.total_processed == 3
    assert len(result.successful_ids) == 1
    assert len(result.failed_ids) == 2
    assert result.success_rate == 1 / 3


def test_batch_update_concurrent(vector_store_dir, test_data):
    """Test concurrent batch updates."""
    search = UnifiedSearch(
        persist_dir=vector_store_dir,
        max_batch_size=2,
        max_workers=4,
    )

    # Create initial index
    search.create_index(
        texts=test_data["texts"],
        collection_name="test_collection",
        metadata=test_data["metadata"],
    )

    # Prepare large update batch
    update_texts = [f"Text {i}" for i in range(10)]
    update_metadata = [{"faq_id": str(i + 100), "category": "TEST"} for i in range(10)]

    # Perform batch update
    result = search.batch_update(
        collection_name="test_collection",
        texts=update_texts,
        metadata=update_metadata,
    )

    # Verify results
    assert result.total_processed == 10
    assert len(result.successful_ids) == 10
    assert len(result.failed_ids) == 0
    assert result.success_rate == 1.0

    # Verify processing time is recorded
    assert result.processing_time > 0
