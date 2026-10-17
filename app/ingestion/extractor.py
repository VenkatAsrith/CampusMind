"""Text extractors for PDF, DOCX, and plain text files with metadata preservation."""

import io
from typing import Any, Dict, List, Optional
import pypdf
import docx

from app.core.exceptions import IngestionError
from app.ingestion.cleaner import clean_text


def extract_from_pdf(content: bytes) -> List[Dict[str, Any]]:
    """Extract text from PDF pages preserving page numbers."""
    sections: List[Dict[str, Any]] = []
    try:
        reader = pypdf.PdfReader(io.BytesIO(content))
        total_pages = len(reader.pages)
        if total_pages == 0:
            raise IngestionError("PDF contains no pages")

        for page_idx, page in enumerate(reader.pages):
            page_num = page_idx + 1
            raw_text = page.extract_text() or ""
            cleaned = clean_text(raw_text)
            if cleaned:
                sections.append({
                    "text": cleaned,
                    "page_number": page_num,
                    "section_heading": f"Page {page_num}",
                })
    except Exception as exc:
        raise IngestionError(f"Failed to extract text from PDF: {str(exc)}")

    if not sections:
        raise IngestionError("PDF contains no readable text or is scanned/encrypted without OCR")
    return sections


def extract_from_docx(content: bytes) -> List[Dict[str, Any]]:
    """Extract text from DOCX preserving headings and paragraphs."""
    sections: List[Dict[str, Any]] = []
    try:
        doc = docx.Document(io.BytesIO(content))
        current_heading = "General"
        current_paragraphs: List[str] = []

        for p in doc.paragraphs:
            text = clean_text(p.text)
            if not text:
                continue

            # Check if paragraph style is a heading
            if p.style and p.style.name.startswith("Heading"):
                if current_paragraphs:
                    sections.append({
                        "text": "\n\n".join(current_paragraphs),
                        "page_number": None,
                        "section_heading": current_heading,
                    })
                    current_paragraphs = []
                current_heading = text
            else:
                current_paragraphs.append(text)

        if current_paragraphs:
            sections.append({
                "text": "\n\n".join(current_paragraphs),
                "page_number": None,
                "section_heading": current_heading,
            })
    except Exception as exc:
        raise IngestionError(f"Failed to extract text from DOCX: {str(exc)}")

    if not sections:
        raise IngestionError("DOCX document contains no readable text")
    return sections


def extract_from_txt(content: bytes) -> List[Dict[str, Any]]:
    """Extract text from plain text or markdown files."""
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = content.decode("latin-1")
        except Exception as exc:
            raise IngestionError(f"Failed to decode text file: {str(exc)}")

    cleaned = clean_text(text)
    if not cleaned:
        raise IngestionError("Text file is empty or contains only whitespace")

    sections: List[Dict[str, Any]] = []
    lines = cleaned.split("\n")
    current_heading = "Overview"
    current_lines: List[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            if current_lines:
                sections.append({
                    "text": "\n".join(current_lines).strip(),
                    "page_number": 1,
                    "section_heading": current_heading,
                })
                current_lines = []
            current_heading = stripped.lstrip("#").strip()
        else:
            current_lines.append(line)

    if current_lines:
        sections.append({
            "text": "\n".join(current_lines).strip(),
            "page_number": 1,
            "section_heading": current_heading,
        })

    return sections


def extract_document_text(extension: str, content: bytes) -> List[Dict[str, Any]]:
    """Route document content to the appropriate extractor based on extension."""
    ext = extension.lower().lstrip(".")
    if ext == "pdf":
        return extract_from_pdf(content)
    elif ext == "docx":
        return extract_from_docx(content)
    elif ext in ("txt", "md"):
        return extract_from_txt(content)
    else:
        raise IngestionError(f"Unsupported document format for extraction: '{ext}'")
