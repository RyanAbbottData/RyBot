import json
import platform

from datetime import datetime
import os
from typing import List
import anthropic
from dotenv import load_dotenv

from models.kb_entry import KBEntry
from models.raw_doc import RawDocument
from prompts.kb_extraction_prompt import KB_EXTRACTION_SYSTEM_PROMPT


# Several platform module calls hang on Python 3.13 + Windows 11.
# The Anthropic SDK calls them on every request to build X-Stainless-* headers.
if not hasattr(platform, "_stainless_patched"):
    platform.platform = lambda *_: "Windows-11"
    platform.system = lambda: "Windows"
    platform.machine = lambda: "AMD64"
    platform.python_version = lambda: "3.13.3"
    platform.python_implementation = lambda: "CPython"
    platform._stainless_patched = True

# Loading env secret variables
load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")

def extract_kb_entries_from_document(
    doc: RawDocument,
    max_text_chars: int = 12000,
) -> List[KBEntry]:
    """
    Send a RawDocument to Claude and extract structured KB entries.

    Args:
        doc            : The parsed document
        client         : Anthropic API client
        max_text_chars : Truncate very long docs to keep within token budget

    Returns:
        List of KBEntry objects validated against the ontology schema
    """

    # Initializing antrhopic client
    client = anthropic.Anthropic(api_key=API_KEY, timeout=30.0, max_retries=0)

    # Truncate very long documents — most policy docs are well under 12k chars
    text = doc.text[:max_text_chars]
    if len(doc.text) > max_text_chars:
        text += "\n\n[Document truncated — first 12,000 characters shown]"

    user_message = f"""Document filename: {doc.filename}
Source: {doc.source} — {doc.source_path}
Last modified: {doc.last_modified}

--- DOCUMENT TEXT ---
{text}
--- END DOCUMENT ---

Extract all knowledge base entries from this document."""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        system=KB_EXTRACTION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_output = response.content[0].text.strip()

    # Strip markdown code fences if Claude added them despite instructions
    if raw_output.startswith("```"):
        raw_output = raw_output.split("\n", 1)[1]
        if raw_output.endswith("```"):
            raw_output = raw_output.rsplit("```", 1)[0]

    # Parse and validate
    entries_raw = json.loads(raw_output)
    entries = []
    now = datetime.utcnow().isoformat() + "Z"

    for raw in entries_raw:
        category = raw.get("category", "").strip()
        key      = raw.get("key", "").strip()

        # Validate category against ontology
        # if category not in VALID_KB_CATEGORIES:
        #     print(f"    ⚠ Skipped invalid category '{category}' (key: {key})")
        #     continue

        if not key:
            print(f"    ⚠ Skipped entry with empty key in category '{category}'")
            continue

        entries.append(KBEntry(
            entry_id      = f"{category}.{key}",
            category      = category,
            key           = key,
            value         = raw.get("value"),
            data_type     = raw.get("data_type", "string"),
            source_doc_id = doc.doc_id,
            source_path   = doc.source_path,
            valid_from    = now,
            confidence    = raw.get("confidence", "medium"),
            notes         = raw.get("notes", ""),
        ))

    return entries