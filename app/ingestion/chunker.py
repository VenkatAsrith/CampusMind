"""Semantic text chunking with metadata preservation."""

from typing import Any, Dict, List
from app.core.config import settings


def split_text_into_chunks(
    text: str,
    chunk_size: int = settings.CHUNK_SIZE,
    chunk_overlap: int = settings.CHUNK_OVERLAP,
) -> List[str]:
    """Split text into overlapping chunks respecting sentence and paragraph boundaries."""
    if not text or not text.strip():
        return []

    text = text.strip()
    if len(text) <= chunk_size:
        return [text]

    chunks: List[str] = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size

        if end >= text_len:
            chunks.append(text[start:].strip())
            break

        # Look for semantic break points (paragraph, sentence, punctuation, or space)
        break_pos = -1
        window = text[start:end]

        # 1. Paragraph boundary
        para_idx = window.rfind("\n\n")
        if para_idx != -1 and para_idx >= chunk_size // 3:
            break_pos = start + para_idx + 2
        else:
            # 2. Sentence boundary (. ! ?)
            for punct in [". ", "? ", "! ", ".\n", ";\n"]:
                punct_idx = window.rfind(punct)
                if punct_idx != -1 and punct_idx >= chunk_size // 3:
                    break_pos = start + punct_idx + len(punct)
                    break

            # 3. Word boundary (space)
            if break_pos == -1:
                space_idx = window.rfind(" ")
                if space_idx != -1 and space_idx >= chunk_size // 4:
                    break_pos = start + space_idx + 1
                else:
                    # Hard cut if no suitable boundary found
                    break_pos = end

        chunk = text[start:break_pos].strip()
        if chunk:
            chunks.append(chunk)

        # Advance start position by (break_pos - chunk_overlap)
        next_start = break_pos - chunk_overlap
        if next_start <= start:
            next_start = break_pos
        start = next_start

    return chunks


def chunk_document_sections(sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert extracted document sections into a flat list of chunk dicts with indices and metadata."""
    all_chunks: List[Dict[str, Any]] = []
    current_idx = 0

    for section in sections:
        section_text = section.get("text", "")
        page_num = section.get("page_number")
        heading = section.get("section_heading")

        text_chunks = split_text_into_chunks(section_text)
        for t in text_chunks:
            if not t.strip():
                continue
            all_chunks.append({
                "chunk_index": current_idx,
                "chunk_text": t,
                "page_number": page_num,
                "section_heading": heading,
            })
            current_idx += 1

    return all_chunks
