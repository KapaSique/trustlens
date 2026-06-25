"""Analyst agent: answers business questions by querying data via MCP."""

from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from trustlens.model_config import MODEL, resilient_config

_SERVER = str(Path(__file__).resolve().parents[1] / "mcp_server.py")

INSTRUCTION = (
    "You are a data analyst for an e-commerce business. "
    "First call get_schema to learn the tables and columns. Then, for each figure the "
    "question needs, write a single read-only SELECT that returns ONE numeric scalar and "
    "run it with query_data. Never invent numbers — every figure must come from a "
    "query_data result. If a query is blocked or errors, revise the SQL and retry.\n"
    "Return ONLY a JSON array, one object per figure, each exactly:\n"
    '  {"claim": "<plain-English meaning>", "sql": "<the EXACT scalar SELECT you ran>", '
    '"value": <the number query_data returned>}\n'
    "The sql and value MUST be exactly what you executed and received, so they can be "
    "re-verified. Do not add prose outside the JSON array."
)


def build_analyst(output_key: str | None = None) -> tuple[LlmAgent, McpToolset]:
    """Construct the Analyst agent wired to the TrustLens MCP server over stdio.

    Pass output_key (e.g. "findings") to save the analyst's output to session
    state for a downstream agent in a SequentialAgent pipeline.
    """
    toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="python3",
                args=[_SERVER],
            ),
        ),
        tool_filter=["get_schema", "query_data"],
    )
    agent = LlmAgent(
        model=MODEL,
        name="analyst",
        instruction=INSTRUCTION,
        tools=[toolset],
        output_key=output_key,
        generate_content_config=resilient_config(),
    )
    return agent, toolset
