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
    "To answer a question, first call get_schema to learn the tables and columns, "
    "then write a single read-only SELECT query and call query_data. "
    "Never invent numbers — every figure must come from a query_data result. "
    "If a query is blocked or returns an error, revise the SQL and try again. "
    "Answer concisely with the figures you retrieved."
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
