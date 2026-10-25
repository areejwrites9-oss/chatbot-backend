from __future__ import annotations

import logging
import time

from app.embeddings import generate_query_embedding
from app.qdrant_db import search_relevant_chunks

logger = logging.getLogger(__name__)


def retrieve_relevant_context(question: str, top_k: int = 2) -> dict[str, object]:
    """Create a query embedding and retrieve the most relevant chunks from Qdrant."""
    cleaned_question = question.strip()
    if not cleaned_question:
        return {"context": "", "sources": []}

    retrieval_started = time.perf_counter()
    embedding_started = time.perf_counter()
    query_vector = generate_query_embedding(cleaned_question)
    embedding_elapsed = time.perf_counter() - embedding_started

    search_started = time.perf_counter()
    matches = search_relevant_chunks(query_vector, top_k=top_k)
    search_elapsed = time.perf_counter() - search_started
    logger.info(
        "Retrieval timing: query_embedding=%.3fs qdrant_search=%.3fs total=%.3fs",
        embedding_elapsed,
        search_elapsed,
        time.perf_counter() - retrieval_started,
    )

    if not matches:
        return {"context": "", "sources": []}

    context_parts = []
    sources = []
    for match in matches:
        text = match.get("text", "")
        source = match.get("source", "unknown")
        score = match.get("score")

        context_parts.append(f"[Source: {source}]\n{text}")
        sources.append({"source": source, "score": score})

    return {
        "context": "\n\n---\n\n".join(context_parts),
        "sources": sources,
    }
