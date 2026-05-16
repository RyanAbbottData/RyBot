import io
from pathlib import Path
from datetime import datetime

import pdfplumber
from markdown_it import MarkdownIt
import numpy as np

from models.raw_doc import RawDocument


def parse_pdf(file_path: str, source: str = "local") -> RawDocument:
    """Extract text from a PDF. Handles multi-column layouts page by page."""

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            page_text = page.extract_text()
            if page_text and page_text.strip():
                text_parts.append(f"[Page {page_num}]\n{page_text.strip()}")

    raw_text = "\n\n".join(text_parts)

    DOC_ID = np.random.randint(100000, 1000000)
    PATH = Path(file_path)
    FILE_TYPE = "pdf"
    CURRENT_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    FILE_SIZE = len(file_bytes)

    raw_doc = RawDocument(
        doc_id=DOC_ID,
        source=source,
        source_path=file_path,
        filename=PATH.name,
        file_type=FILE_TYPE,
        text=raw_text,
        last_modified=CURRENT_TIME,
        size_bytes=FILE_SIZE
    )


    return raw_doc

def parse_md(file_path: str, source: str = "local") -> RawDocument:
    with open(file_path, "rb") as f:
        raw_text = f.read()

    DOC_ID = np.random.randint(100000, 1000000)
    PATH = Path(file_path)
    FILE_TYPE = "md"
    CURRENT_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    FILE_SIZE = len(raw_text)

    raw_doc = RawDocument(
        doc_id=DOC_ID,
        source=source,
        source_path=file_path,
        filename=PATH.name,
        file_type=FILE_TYPE,
        text=raw_text,
        last_modified=CURRENT_TIME,
        size_bytes=FILE_SIZE
    )

    return raw_doc