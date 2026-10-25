from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import app.generator as generator


def test_generate_answer_uses_groq_with_question_and_context(monkeypatch):
    client = Mock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content="Answer from Groq.")
            )
        ]
    )
    monkeypatch.setattr(
        generator,
        "get_settings",
        lambda: {"groq_generation_model": "openai/gpt-oss-20b"},
    )
    monkeypatch.setattr(generator, "_get_client", lambda: client)

    answer = generator.generate_answer("What is RAG?", "RAG is retrieval-augmented generation.")

    assert answer == "Answer from Groq."
    call = client.chat.completions.create.call_args.kwargs
    assert call["model"] == "openai/gpt-oss-20b"
    assert call["messages"][1]["content"].startswith("User question: What is RAG?")
    assert "RAG is retrieval-augmented generation." in call["messages"][1]["content"]


def test_generate_answer_reports_empty_groq_response(monkeypatch):
    client = Mock()
    client.chat.completions.create.return_value = SimpleNamespace(choices=[])
    monkeypatch.setattr(
        generator,
        "get_settings",
        lambda: {"groq_generation_model": "openai/gpt-oss-20b"},
    )
    monkeypatch.setattr(generator, "_get_client", lambda: client)

    with pytest.raises(RuntimeError, match="Groq returned an empty response"):
        generator.generate_answer("What is RAG?", "RAG context")
