from __future__ import annotations

from typing import Sequence

from google import genai
from google.genai import types

from app.config import get_settings


def _get_client() -> genai.Client:
    settings = get_settings()
    return genai.Client(api_key=settings["gemini_api_key"])


def generate_embedding(
    text: str,
    model_name: str | None = None,
    task_type: str = "RETRIEVAL_DOCUMENT",
) -> list[float]:
    if not text or not text.strip():
        raise ValueError("Text must not be empty before embedding.")

    settings = get_settings()
    chosen_model = model_name or settings["gemini_embedding_model"]

    try:
        client = _get_client()
        result = client.models.embed_content(
            model=chosen_model,
            contents=text,
            config=types.EmbedContentConfig(task_type=task_type),
        )
    except Exception as exc:  # pragma: no cover - depends on live API service
        raise RuntimeError(f"Failed to generate embedding with model {chosen_model}.") from exc

    try:
        embedding = result.embeddings[0].values
    except (AttributeError, IndexError, TypeError):
        raise RuntimeError("Unexpected Gemini embedding response format.")

    return list(embedding)


def generate_embeddings(
    texts: Sequence[str],
    model_name: str | None = None,
    task_type: str = "RETRIEVAL_DOCUMENT",
) -> list[list[float]]:
    if not texts:
        return []

    settings = get_settings()
    chosen_model = model_name or settings["gemini_embedding_model"]
    client = _get_client()

    try:
        result = client.models.embed_content(
            model=chosen_model,
            contents=list(texts),
            config=types.EmbedContentConfig(task_type=task_type),
        )
    except Exception as exc:  # pragma: no cover - depends on live API service
        raise RuntimeError(f"Failed to generate embeddings with model {chosen_model}.") from exc

    vectors = []
    try:
        for item in result.embeddings:
            vectors.append(list(item.values))
    except AttributeError as exc:
        raise RuntimeError("Unexpected Gemini embedding response format for multiple texts.") from exc

    return vectors


def generate_query_embedding(question: str, model_name: str | None = None) -> list[float]:
    return generate_embedding(question, model_name=model_name, task_type="RETRIEVAL_QUERY")
