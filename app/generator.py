from __future__ import annotations

import logging
import time

from groq import Groq

from app.config import get_settings
from app.prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def _get_client() -> Groq:
    settings = get_settings()
    return Groq(api_key=settings["groq_api_key"])


def generate_answer(question: str, context: str) -> str:
    """Send the user question and retrieved context to Groq to generate the final answer."""
    cleaned_question = question.strip()
    if not cleaned_question:
        raise ValueError("Question must not be empty.")

    if not context or not context.strip():
        return "I could not find enough relevant information in the knowledge base to answer that question."

    settings = get_settings()
    model_name = settings["groq_generation_model"]
    generation_started = time.perf_counter()

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"User question: {cleaned_question}\n\n"
                        f"Retrieved context:\n{context}"
                    ),
                },
            ],
        )
    except Exception as exc:  # pragma: no cover - depends on live API service
        logger.exception(
            "Groq generation failed for model %s after %.3fs",
            model_name,
            time.perf_counter() - generation_started,
        )
        raise RuntimeError("Failed to generate a Groq response for the provided context.") from exc

    answer = response.choices[0].message.content if response.choices else None
    if answer and answer.strip():
        logger.info(
            "Groq generation timing: model=%s elapsed=%.3fs",
            model_name,
            time.perf_counter() - generation_started,
        )
        return answer

    raise RuntimeError("Groq returned an empty response.")
