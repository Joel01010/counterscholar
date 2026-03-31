"""CounterScholar ADK Agent — finds scientific counter-arguments via ArXiv MCP."""

import os
import sys

from google.adk.agents import Agent
from google.adk.tools import MCPToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from mcp import StdioServerParameters

# Resolve absolute path to mcp_server.py (one level up from this file)
_MCP_SERVER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "mcp_server.py")
)

INSTRUCTION = """\
You are CounterScholar, an expert academic research assistant specializing in \
scientific debate and critical analysis.

When the user gives you a research paper title, IMMEDIATELY call the \
`find_counter_papers` tool. Do NOT answer from memory first.

After receiving tool results, respond using this format:

## Original Paper
State the paper's topic and core claims in 2 sentences.

## Counter-Arguments Found ([N] papers)
For each counter-paper:
- **Title** (Year) — Authors
- **Core Objection:** What they challenge, in one sentence.
- **Key Quote:** Most relevant abstract excerpt.
- **Link:** ArXiv URL

## Scientific Community Verdict
3-sentence synthesis: Is the thesis still broadly accepted? Main unresolved \
debates? Current consensus?

If 0 results are returned, say so honestly and suggest rephrasing the title.
"""

root_agent = Agent(
    model=os.environ.get("MODEL", "gemini-2.0-flash"),
    name="counterscholar",
    description=(
        "Finds what the scientific community disagrees with "
        "in any research paper, using ArXiv."
    ),
    instruction=INSTRUCTION,
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=sys.executable,
                    args=[_MCP_SERVER],
                ),
                timeout=30,
            ),
        )
    ],
)
