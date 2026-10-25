from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Question to ask the chatbot.")


class SourceReference(BaseModel):
    source: str
    score: Optional[float] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceReference] = Field(default_factory=list)


class IngestResponse(BaseModel):
    documents_processed: int
    chunks_processed: int
    vectors_stored: int


class IngestSummary(BaseModel):
    documents_processed: int
    chunks_processed: int
    vectors_stored: int
