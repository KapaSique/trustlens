"""TrustLens MCP server — read-only data tools over the Olist SQLite db.

Run standalone:
  uv run python src/trustlens/mcp_server.py
ADK connects to this over stdio via McpToolset (see agents/analyst.py).
"""

import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from trustlens import db
from trustlens.security import SecurityError, check_query

DB_PATH = os.environ.get(
    "TRUSTLENS_DB",
    str(Path(__file__).resolve().parents[2] / "data" / "trustlens.db"),
)

mcp = FastMCP("trustlens-data")


@mcp.tool()
def get_schema() -> str:
    """List all tables and their columns in the business database (JSON)."""
    return json.dumps(db.get_schema(DB_PATH))


@mcp.tool()
def query_data(sql: str) -> str:
    """Run a read-only SELECT query and return rows as JSON.

    Only SELECT is permitted; mutations, multiple statements, and PII columns
    are blocked. Returns {"rows": [...]} on success or {"error": "..."} on
    rejection so the agent can revise its SQL.
    """
    try:
        check_query(sql)
        rows = db.read_query(DB_PATH, sql).to_dict(orient="records")
        return json.dumps({"rows": rows})
    except SecurityError as e:
        return json.dumps({"error": f"blocked: {e}"})
    except Exception as e:  # malformed SQL, missing table, etc.
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run(transport="stdio")
