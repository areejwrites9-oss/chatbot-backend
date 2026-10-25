from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)


def _require_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or not value.strip():
        raise ValueError(f"Missing required environment variable: {name}")
    return value.strip()


@lru_cache
def get_settings() -> dict[str, str | None]:
    settings = {
        "gemini_api_key": _require_env("GEMINI_API_KEY"),
        "gemini_embedding_model": _require_env(
            "GEMINI_EMBEDDING_MODEL",
            "gemini-embedding-001",
        ),
        "groq_api_key": _require_env("GROQ_API_KEY"),
        "groq_generation_model": _require_env(
            "GROQ_GENERATION_MODEL",
            "openai/gpt-oss-20b",
        ),
        "qdrant_url": _require_env("QDRANT_URL", "http://localhost:6333"),
        "qdrant_api_key": os.getenv("QDRANT_API_KEY") or None,
        "qdrant_collection_name": _require_env(
            "QDRANT_COLLECTION_NAME",
            "chatbot_knowledge",
        ),
        "frontend_origin": _require_env("FRONTEND_ORIGIN", "http://localhost:5173"),
        "chunk_size": os.getenv("CHUNK_SIZE", "500"),
        "chunk_overlap": os.getenv("CHUNK_OVERLAP", "80"),
        "data_dir": str(BASE_DIR / "data"),
    }
    return settings


DATA_DIR = BASE_DIR / "data"
