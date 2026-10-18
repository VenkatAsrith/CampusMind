"""Document upload validation and filename sanitization."""

import hashlib
import os
import re
from typing import Tuple
from app.core.config import settings
from app.core.exceptions import ValidationError


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and shell injection attacks."""
    # Strip directory components
    base_name = os.path.basename(filename)
    # Remove null bytes and path separators
    clean = re.sub(r"[\x00/\\:\*\?\"<>\|]", "_", base_name)
    # Strip leading dots to prevent hidden files
    clean = clean.lstrip(".")
    if not clean:
        clean = "document_upload"
    return clean


def validate_uploaded_file(filename: str, content: bytes) -> Tuple[str, str, str, int]:
    """Validate file size, extension, non-emptiness, and compute SHA-256 hash.

    Returns:
        (sanitized_filename, extension, content_hash, file_size_bytes)
    """
    if not content or len(content.strip()) == 0:
        raise ValidationError("Uploaded file is empty")

    file_size = len(content)
    if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
        max_mb = settings.MAX_UPLOAD_SIZE_BYTES / (1024 * 1024)
        raise ValidationError(f"File size exceeds limit of {max_mb:.1f} MB (got {file_size / (1024 * 1024):.2f} MB)")

    clean_filename = sanitize_filename(filename)
    _, ext = os.path.splitext(clean_filename)
    clean_ext = ext.lower().lstrip(".")

    allowed = settings.allowed_extensions
    if clean_ext not in allowed:
        raise ValidationError(f"Unsupported file type '{clean_ext}'. Supported formats: {', '.join(allowed)}")

    content_hash = hashlib.sha256(content).hexdigest()
    return clean_filename, clean_ext, content_hash, file_size
