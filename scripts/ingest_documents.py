from __future__ import annotations

from app.ingest import ingest_documents


def main() -> None:
    summary = ingest_documents()
    print("Ingestion complete.")
    print(f"Documents processed: {summary['documents_processed']}")
    print(f"Chunks processed: {summary['chunks_processed']}")
    print(f"Vectors stored: {summary['vectors_stored']}")


if __name__ == "__main__":
    main()
