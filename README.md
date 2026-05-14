# RyBot

**An AI-powered personal assistant built on RAG + Model Context Protocol**

![Python](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python&logoColor=white)
![Anthropic SDK](https://img.shields.io/badge/Anthropic%20SDK-0.100.0-blueviolet?logo=anthropic)
![FastMCP](https://img.shields.io/badge/FastMCP-1.27.1-orange)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Cross--platform-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Overview

RyBot is a production-grade AI assistant that answers questions about me — my education, career experience, and professional strengths — by combining **Retrieval-Augmented Generation (RAG)** with Anthropic's **Model Context Protocol (MCP)**.

Rather than hard-coding facts into a prompt, RyBot uses a two-phase approach: first, it intelligently extracts structured knowledge from real source documents (PDFs) using Claude; then, it serves that knowledge through a live MCP server that any Claude-compatible client can query via tool calls. The result is a system that gives accurate, grounded answers that are fully traceable back to their source documents.

This project was built to demonstrate a full-cycle ML/AI engineering workflow — from document ingestion and structured extraction, to API design, server deployment, and public tunneling — using the same tools and patterns found in production AI systems.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Phase 1: Ingestion                     │
│                                                         │
│  PDF Docs  ──▶  pdfplumber  ──▶  Claude (extraction)   │
│  (docs/)         (parse)       (structured JSON)        │
│                                    │                    │
│                                    ▼                    │
│                          Pydantic Validation            │
│                                    │                    │
│                                    ▼                    │
│                         JSON Knowledge Base (kb/)       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  Phase 2: Serving                       │
│                                                         │
│  MCP Client  ──▶  FastMCP Server  ──▶  Tool Dispatch   │
│  (Claude.ai,      (HTTP / SSE)        (lookup_*)        │
│   Claude Code,         │                    │           │
│   any MCP app)         │                    ▼           │
│                        │          JSON Knowledge Base   │
│                        │                    │           │
│                        ▼                    ▼           │
│               Cloudflare Tunnel       Structured        │
│               (public HTTPS URL)       Response         │
└─────────────────────────────────────────────────────────┘
```

---

## Features

RyBot exposes three MCP tools that any Claude client can call:

| Tool | What it answers |
|------|----------------|
| `lookup_schooling_information()` | K-12 schools, University of Oklahoma (Astrophysics, GPA 3.62, Data Science certificate), graduation honors |
| `lookup_resume_info()` | Professional experience, ML skills, cloud platforms, DevOps tooling, data engineering stack |
| `lookup_strengths()` | High-impact work stories — automation wins, architecture redesigns, testing infrastructure |

Each tool returns structured, confidence-scored data extracted directly from source documents, with full audit trails (source file + page references).

---

## Tech Stack

| Category | Technology | Role |
|----------|-----------|------|
| **LLM / AI** | Anthropic Claude (claude-sonnet-4-6) | Knowledge extraction & conversational AI |
| **MCP Framework** | FastMCP 1.27.1 | MCP server definition, tool registration, SSE transport |
| **API Server** | Uvicorn + Starlette | ASGI server hosting the MCP HTTP endpoint |
| **Document Parsing** | pdfplumber, pdfminer.six | PDF text extraction pipeline |
| **Data Validation** | Pydantic v2 | Schema enforcement for KB entries |
| **Knowledge Storage** | JSON (local filesystem) | Lightweight, inspectable KB persistence |
| **Tunneling** | Cloudflare Tunnel (`cloudflared`) | Secure public HTTPS access to local server |
| **Config** | python-dotenv | Environment variable management |
| **Language** | Python 3.13 | Core runtime |

---

## How It Works

### Knowledge Extraction Pipeline

1. **Parse** — `pdfplumber` reads each PDF in `docs/` and extracts raw text (up to 12,000 characters per document).
2. **Extract** — The raw text is sent to Claude with a structured extraction prompt. Claude returns a list of `KBEntry` objects: each entry has a `fact`, `category`, `confidence` score (`high` / `medium` / `low`), and `source` reference.
3. **Validate** — Pydantic models enforce schema correctness before anything is written to disk.
4. **Persist** — Validated entries are saved to category-specific JSON files under `kb/` (e.g., `kb/resume.json`, `kb/schooling.json`).

Run this pipeline any time source documents change:
```bash
python add_to_kb.py
```

### MCP Server

The server is built with **FastMCP**, which turns plain Python functions into MCP-compliant tools with zero boilerplate. It runs over HTTP with Server-Sent Events (SSE) so any MCP-capable client (Claude.ai, Claude Code, custom apps) can connect and call tools in real time.

```python
@mcp.tool()
def lookup_resume_info() -> list[KBEntry]:
    """Returns structured professional experience and skills."""
    return load_kb("resume")
```

Start the server:
```bash
python mcp_server.py        # localhost:8000
```

Expose it publicly via Cloudflare Tunnel:
```bash
tunnel.bat                  # generates a public HTTPS URL, no account required
```

---

## Demo

> **Live demo available on request.**
>
> The server runs locally and is exposed via Cloudflare Tunnel when active. Permanent cloud hosting (Railway / Render) is planned for a future release. Reach out via [LinkedIn](https://www.linkedin.com/in/ryanabbottdata) or open an issue to schedule a live walkthrough.

---

## Project Structure

```
RyBot/
├── mcp_server.py          # FastMCP server — tool definitions & entry point
├── add_to_kb.py           # Ingestion pipeline — PDFs → knowledge base
│
├── models/
│   ├── raw_doc.py         # RawDocument schema (parsed PDF content)
│   └── kb_entry.py        # KBEntry schema (extracted fact + metadata)
│
├── utils/
│   ├── parse_docs.py      # PDF parsing logic (pdfplumber)
│   └── knowledge_base.py  # Claude extraction + KB write logic
│
├── prompts/
│   └── kb_extraction_prompt.py  # System prompt for structured extraction
│
├── kb/                    # Knowledge base (auto-generated JSON)
│   ├── schooling.json
│   ├── resume.json
│   └── strengths.json
│
├── docs/                  # Source PDF documents
├── run.bat                # One-click server start (activates venv)
├── tunnel.bat             # One-click Cloudflare tunnel
└── .env                   # API keys (not committed)
```

---

## Getting Started

**Prerequisites:** Python 3.13+, an [Anthropic API key](https://console.anthropic.com)

```bash
# 1. Clone the repo
git clone https://github.com/RyanAbbottData/RyBot.git
cd RyBot

# 2. Create and activate a virtual environment
python -m venv rybot_venv
rybot_venv\Scripts\activate       # Windows
# source rybot_venv/bin/activate  # macOS / Linux

# 3. Install dependencies
pip install anthropic fastmcp pydantic pdfplumber python-dotenv uvicorn starlette

# 4. Configure your API key
echo ANTHROPIC_API_KEY=your_key_here > .env

# 5. (Optional) Re-ingest documents to rebuild the knowledge base
python add_to_kb.py

# 6. Start the MCP server
python mcp_server.py
# Server runs at http://localhost:8000

# 7. (Optional) Expose publicly via Cloudflare Tunnel
tunnel.bat
```

Connect any MCP-compatible client to `http://localhost:8000` (or the tunnel URL) and start querying.

---

## Roadmap

- [ ] Web UI / chat interface (Next.js or Streamlit)
- [ ] Permanent cloud hosting (Railway or Render)
- [ ] Additional KB categories (personal projects, interests, open-source contributions)
- [ ] Conversational memory across sessions
- [ ] `requirements.txt` for one-command dependency install

---

## Author

**Ryan Abbott** — ML Engineer & Data Scientist

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/ryanabbottdata)
[![GitHub](https://img.shields.io/badge/GitHub-RyanAbbottData-181717?logo=github&logoColor=white)](https://github.com/RyanAbbottData)
