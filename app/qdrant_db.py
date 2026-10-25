from __future__ import annotations

import hashlib
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.config import get_settings


def get_qdrant_client() -> QdrantClient:
    settings = get_settings()
    client_kwargs: dict[str, Any] = {
        "url": settings["qdrant_url"],
        "timeout": 60,
    }
    if settings.get("qdrant_api_key"):
        client_kwargs["api_key"] = settings["qdrant_api_key"]

    return QdrantClient(**client_kwargs)


def get_vector_size(model_name: str | None = None) -> int:
    settings = get_settings()
    embedding_model = (model_name or settings["gemini_embedding_model"]).strip()
    size_map = {
        "gemini-embedding-001": 3072,
        "text-embedding-004": 768,
        "text-embedding-005": 768,
    }
    return size_map.get(embedding_model, 3072)


def stable_point_id(document_name: str, chunk_index: int) -> int:
    key = f"{document_name}:{chunk_index}".encode("utf-8")
    digest = hashlib.md5(key).hexdigest()
    return int(digest[:16], 16) % (2**63 - 1)


def ensure_collection(client: QdrantClient | None = None) -> str:
    settings = get_settings()
    client = client or get_qdrant_client()
    collection_name = settings["qdrant_collection_name"]

    existing_collections = client.get_collections().collections
    names = [item.name for item in existing_collections]

    if collection_name not in names:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=get_vector_size(settings["gemini_embedding_model"]),
                distance=models.Distance.COSINE,
            ),
        )
        return collection_name

    collection = client.get_collection(collection_name)
    params = getattr(getattr(collection, "config", None), "params", None)
    vectors = getattr(params, "vectors", None)

    if vectors is not None and getattr(vectors, "size", None) is not None:
        expected_size = get_vector_size(settings["gemini_embedding_model"])
        if vectors.size != expected_size:
            raise ValueError(
                "Qdrant collection already exists with a different vector size. "
                f"Expected {expected_size}, found {vectors.size}."
            )

    return collection_name


def upsert_document_chunks(chunks: list[dict[str, Any]]) -> int:
    if not chunks:
        return 0

    settings = get_settings()
    client = get_qdrant_client()
    collection_name = ensure_collection(client)

    points = []
    for item in chunks:
        if not item.get("text", "").strip():
            continue

        points.append(
            models.PointStruct(
                id=stable_point_id(item["document_name"], item["chunk_index"]),
                vector=item["embedding"],
                payload={
                    "text": item["text"],
                    "source": item["document_name"],
                    "chunk_index": item["chunk_index"],
                },
            )
        )

    if not points:
        return 0

    client.upsert(collection_name=collection_name, points=points, wait=True)
    return len(points)


def search_relevant_chunks(query_vector: list[float], top_k: int = 2) -> list[dict[str, Any]]:
    client = get_qdrant_client()
    collection_name = ensure_collection(client)

    results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    ).points

    matches: list[dict[str, Any]] = []
    for hit in results:
        payload = hit.payload or {}
        matches.append(
            {
                "text": payload.get("text", ""),
                "source": payload.get("source", "unknown"),
                "score": float(hit.score) if hasattr(hit, "score") else None,
            }
        )

    return matches
