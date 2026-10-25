from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config import DATA_DIR


def load_markdown_documents(data_dir: str | Path | None = None) -> list[dict[str, Any]]:
    """Load all Markdown files from the backend data directory."""
    target_dir = Path(data_dir) if data_dir is not None else DATA_DIR

    if not target_dir.exists():
        raise FileNotFoundError(f"Knowledge base directory does not exist: {target_dir}")

    files = sorted(target_dir.glob("*.md"))
    if not files:
        raise FileNotFoundError(f"No Markdown files were found in: {target_dir}")

    documents: list[dict[str, Any]] = []
    for file_path in files:
        if not file_path.is_file():
            continue

        text = file_path.read_text(encoding="utf-8")
        if not text.strip():
            raise ValueError(f"Markdown file is empty: {file_path.name}")

        documents.append(
            {
                "filename": file_path.name,
                "path": str(file_path),
                "content": text,
            }
        )

    return documents
