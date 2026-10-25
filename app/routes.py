from __future__ import annotations

import logging
import time

from fastapi import APIRouter, HTTPException

from app.generator import generate_answer
from app.ingest import ingest_documents
from app.retriever import retrieve_relevant_context
from app.schemas import ChatRequest, ChatResponse, IngestResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "rag-chatbot-backend"}


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    request_started = time.perf_counter()
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        retrieval = retrieve_relevant_context(question, top_k=2)
        context = retrieval.get("context", "")
        sources = retrieval.get("sources", [])

        if not context:
            answer = "I could not find enough relevant information in the knowledge base to answer that question."
        else:
            try:
                answer = generate_answer(question, str(context))
            except RuntimeError as exc:
                raise HTTPException(status_code=500, detail=str(exc)) from exc

        return ChatResponse(answer=answer, sources=sources)
    finally:
        logger.info(
            "Chat request timing: total=%.3fs",
            time.perf_counter() - request_started,
        )


@router.post("/ingest", response_model=IngestResponse)
def ingest() -> IngestResponse:
    try:
        summary = ingest_documents()
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return IngestResponse(**summary)
