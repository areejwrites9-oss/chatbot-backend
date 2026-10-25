from __future__ import annotations

from app.chunking import chunk_text
from app.config import get_settings
from app.document_loader import load_markdown_documents
from app.embeddings import generate_embeddings
from app.qdrant_db import upsert_document_chunks


def ingest_documents(data_dir: str | None = None) -> dict[str, int]:
    """Load Markdown files, split them into chunks, embed them, and store them in Qdrant."""
    settings = get_settings()
    documents = load_markdown_documents(data_dir)

    processed_chunks: list[dict[str, object]] = []

    for document in documents:
        text = document["content"]
        chunks = chunk_text(
            text,
            chunk_size=int(settings.get("chunk_size", 500)),
            chunk_overlap=int(settings.get("chunk_overlap", 80)),
        )

        for chunk_index, chunk in enumerate(chunks):
            processed_chunks.append(
                {
                    "document_name": document["filename"],
                    "chunk_index": chunk_index,
                    "text": chunk,
                }
            )

    embeddings = generate_embeddings([item["text"] for item in processed_chunks])

    points_to_store = []
    for item, vector in zip(processed_chunks, embeddings):
        points_to_store.append(
            {
                "document_name": item["document_name"],
                "chunk_index": item["chunk_index"],
                "text": item["text"],
                "embedding": vector,
            }
        )

    vectors_stored = upsert_document_chunks(points_to_store)

    return {
        "documents_processed": len(documents),
        "chunks_processed": len(processed_chunks),
        "vectors_stored": vectors_stored,
    }
