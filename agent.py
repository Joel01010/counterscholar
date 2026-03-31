import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioConnectionParams,
    StdioServerParameters,
)

_MCP_SERVER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")

INSTRUCTION = """\
You are CounterScholar. When a user gives you a research paper title, \
IMMEDIATELY call find_counter_papers. Never answer from memory first.

Format your response as:
## Original Paper
## Counter-Arguments Found ([N] papers)
  - Title, authors, core objection, key quote, ArXiv link per paper
## Scientific Community Verdict
  3-sentence synthesis of the debate.
If 0 results, say so honestly and suggest rephrasing.
"""

root_agent = LlmAgent(
    model=os.environ.get("MODEL", "gemini-2.5-flash"),
    name="counterscholar",
    description="Finds scientific counter-arguments to research papers using ArXiv.",
    instruction=INSTRUCTION,
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="python3",
                    args=[_MCP_SERVER],
                )
            )
        )
    ],
)
