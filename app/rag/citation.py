"""Citation generation and validation against retrieved evidence."""

from typing import List, Set, Tuple
from app.retrieval.vector_engine import RetrievedChunk
from app.schemas.chat import CitationSchema


def build_citations_from_retrieved_chunks(chunks: List[RetrievedChunk]) -> List[CitationSchema]:
    """Generate verified source citations strictly from retrieved and authorized chunks.

    Guarantees:
    - Never invents document titles, IDs, or page numbers.
    - Only includes sources that were actually retrieved.
    - Deduplicates identical chunk references.
    """
    seen_chunks: Set[int] = set()
    citations: List[CitationSchema] = []

    for chunk in chunks:
        if chunk.chunk_id in seen_chunks:
            continue
        seen_chunks.add(chunk.chunk_id)

        citations.append(
            CitationSchema(
                document_id=chunk.document_id,
                document_title=chunk.document_title,
                page_number=chunk.page_number,
                section_heading=chunk.section_heading,
                chunk_id=chunk.chunk_id,
                similarity_score=chunk.similarity_score,
            )
        )

    return citations
