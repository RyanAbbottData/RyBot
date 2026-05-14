from typing import Any

from pydantic import BaseModel


class KBEntry(BaseModel):
    """
    A single structured knowledge base entry produced by Claude
    from a raw document. Matches the hospitality ontology KB schema.
    """
    entry_id:      str        # Stable key: category + "." + key
    category:      str        # Top-level KB category (matches ontology)
    key:           str        # Sub-key within category
    value:         Any        # The actual fact — string, dict, list, etc.
    data_type:     str        # "string" | "dict" | "list" | "boolean" | "float"
    source_doc_id: int        # doc_id of the RawDocument it came from
    source_path:   str        # Human-readable path for audit trail
    valid_from:    str        # ISO datetime of extraction
    confidence:    str        # "high" | "medium" | "low" — Claude's self-assessment
    notes:         str = ""   # Claude's extraction reasoning / caveats