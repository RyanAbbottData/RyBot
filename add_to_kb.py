import json

from utils.parse_docs import parse_md, parse_pdf
from utils.knowledge_base import extract_kb_entries_from_document


# Parsing documents and converting them into a RawDocument object
# See more regarding the RawDocument object contents in models/
parsed_doc = parse_pdf("docs/MyCode README.pdf")
print(parsed_doc)

# Converting raw document into KB entry
# For now KB lives in local file storage
kb_entry = extract_kb_entries_from_document(parsed_doc)

with open("kb/myCodeProjectDescription.json", "w") as f:
    json.dump([e.model_dump() for e in kb_entry], f, indent=2)


