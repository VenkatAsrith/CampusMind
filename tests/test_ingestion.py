"""Unit tests for document upload validation, extraction, and chunking."""

import pytest
from app.core.exceptions import ValidationError, IngestionError
from app.ingestion.validator import validate_uploaded_file, sanitize_filename
from app.ingestion.cleaner import clean_text
from app.ingestion.extractor import extract_from_txt, extract_document_text
from app.ingestion.chunker import split_text_into_chunks, chunk_document_sections


def test_sanitize_filename_traversal_prevention():
    """Verify path traversal characters are neutralized."""
    assert sanitize_filename("../../../secret.pdf") == "secret.pdf"
    assert sanitize_filename("..\\..\\passwords.txt") == "passwords.txt"
    assert sanitize_filename(".hidden_file.docx") == "hidden_file.docx"
    assert sanitize_filename("") == "document_upload"


def test_validate_uploaded_file_success():
    """Verify valid file returns clean attributes and sha256 hash."""
    content = b"Campus policy document text."
    filename, ext, content_hash, size = validate_uploaded_file("Academic_Calendar.txt", content)

    assert filename == "Academic_Calendar.txt"
    assert ext == "txt"
    assert len(content_hash) == 64
    assert size == len(content)


def test_validate_uploaded_file_rejects_empty():
    """Verify empty file raises ValidationError."""
    with pytest.raises(ValidationError, match="Uploaded file is empty"):
        validate_uploaded_file("empty.txt", b"")


def test_validate_uploaded_file_rejects_unsupported_extension():
    """Verify unsupported formats (e.g. .exe) are rejected."""
    with pytest.raises(ValidationError, match="Unsupported file type"):
        validate_uploaded_file("malicious.exe", b"executable payload")


def test_clean_text_normalization():
    """Verify whitespace and carriage returns are normalized."""
    dirty = "Line 1\r\n\r\n\r\nLine 2 \t  with   extra    spaces.\x00"
    cleaned = clean_text(dirty)
    assert "\r" not in cleaned
    assert "\x00" not in cleaned
    assert "   " not in cleaned
    assert "Line 1\n\nLine 2 with extra spaces." == cleaned


def test_split_text_into_chunks():
    """Verify sliding window chunker splits long text with overlap and preserves sentences."""
    sample = (
        "First sentence of campus policy. "
        "Second sentence describing enrollment procedures. "
        "Third sentence outlining deadline regulations. "
        "Fourth sentence detailing grade appeals. "
        "Fifth sentence summarizing student rights."
    )
    chunks = split_text_into_chunks(sample, chunk_size=80, chunk_overlap=20)
    assert len(chunks) >= 2
    for c in chunks:
        assert len(c) <= 100
        assert len(c.strip()) > 0


def test_extract_and_chunk_txt_sections():
    """Verify markdown headings are parsed into structured sections and chunked."""
    txt_content = b"# Section One\nParagraph one content.\n# Section Two\nParagraph two content."
    sections = extract_from_txt(txt_content)
    assert len(sections) == 2
    assert sections[0]["section_heading"] == "Section One"
    assert sections[1]["section_heading"] == "Section Two"

    chunks = chunk_document_sections(sections)
    assert len(chunks) == 2
    assert chunks[0]["chunk_index"] == 0
    assert chunks[1]["chunk_index"] == 1
    assert chunks[0]["section_heading"] == "Section One"
