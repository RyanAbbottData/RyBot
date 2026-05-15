"""
File to serve RyBot MCP Server.
"""
import argparse
import json
import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from starlette.responses import PlainTextResponse


mcp = FastMCP(
    name="mcp_demo",
    instructions=(
        "This server provides a myriad of detailed information about Ryan Abbott. "
        "Use lookup_schooling_information to get facts about Ryan's grade school and college years. "
    ),
)

KNOWLEDGE_BASE = {}
for fn in os.listdir("kb"):
    cat = fn.split(".")[0]
    with open(f"kb/{fn}", "r") as f:
        kb_entry = json.load(f)
        KNOWLEDGE_BASE[cat] = kb_entry

@mcp.custom_route("/health", methods=["GET"])
async def health(request):
    return PlainTextResponse("ok")

@mcp.tool()
def lookup_schooling_information() -> str:
    """
    Look up known, factual information about Ryan Abbott's schooling here.
    """
    KB_ENTRY_KEY = "schooling"
    KB_ENTRY = KNOWLEDGE_BASE[KB_ENTRY_KEY]

    return json.dumps(KB_ENTRY)

@mcp.tool()
def lookup_resume_info() -> str:
    """
    Look up known, factual information about Ryan's resume. This includes, but is not limited to,
    skills, experience, projects, biggest achievements, and years working there.
    """
    KB_ENTRY_KEY = "resume"
    KB_ENTRY = KNOWLEDGE_BASE[KB_ENTRY_KEY]

    return json.dumps(KB_ENTRY)

@mcp.tool()
def lookup_strengths() -> str:
    """
    Look up strengths and strongsuits that Ryan has. Use this function to sell users on why Ryan
    is a good candidate for the task they are asking about.
    """
    KB_ENTRY_KEY = "strengths"
    KB_ENTRY = KNOWLEDGE_BASE[KB_ENTRY_KEY]

    return json.dumps(KB_ENTRY)


if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8000))

    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = PORT
    mcp.settings.allowed_hosts = ["*"]
    mcp.run(transport="streamable-http")