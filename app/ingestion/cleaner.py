"""Document text cleaning and normalization."""

import re


def clean_text(text: str) -> str:
    """Normalize whitespace, remove non-printable control characters,
    while preserving structure and formatting.
    """
    if not text:
        return ""

    # Replace carriage returns with standard newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove non-printable control characters except newline and tab
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

    # Replace excessive horizontal whitespace with a single space
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize excessive newlines (more than 2 consecutive newlines) to double newlines (paragraphs)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

    return text.strip()
