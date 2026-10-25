from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes import router

# Uvicorn's default logging setup can leave application loggers at WARNING.
logging.basicConfig(level=logging.INFO)

settings = get_settings()

app = FastAPI(
    title="RAG Chatbot API",
    description="Beginner-friendly RAG backend with FastAPI, Gemini, and Qdrant.",
    version="1.0.0",
)

origins = [settings["frontend_origin"], "http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
