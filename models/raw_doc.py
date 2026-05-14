from typing import Any

from pydantic import BaseModel


class RawDocument(BaseModel):
    """
    A parsed document from any source, ready for KB extraction.
    Carries the full text plus provenance so every KB entry can be
    traced back to the file it came from.
    """
    doc_id:       int        # SHA-256 of content — deduplication key
    source:       str        # "sharepoint" | "s3"
    source_path:  str        # Full path / S3 key
    filename:     str        # e.g. "cancellation_policy_2026.pdf"
    file_type:    str        # ".pdf" | ".docx" | ".txt" etc.
    text:         str        # Full extracted plain text
    last_modified: str       # ISO datetime string
    size_bytes:   int
