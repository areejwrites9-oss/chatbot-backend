from app.chunking import chunk_text


def test_chunk_text_creates_overlapping_chunks():
    text = "alpha beta gamma delta epsilon zeta eta theta"
    chunks = chunk_text(text, chunk_size=20, chunk_overlap=5)

    assert len(chunks) > 1
    assert all(len(chunk) <= 20 for chunk in chunks)
    assert chunks[0][-5:] == chunks[1][:5]


def test_chunk_text_handles_empty_input():
    assert chunk_text("") == []
    assert chunk_text("   ") == []
