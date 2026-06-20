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
from trustlens.audit import audit_append
from trustlens.security import SecurityError, check_query

DB_PATH = os.environ.get(
    "TRUSTLENS_DB",
    str(Path(__file__).resolve().parents[2] / "data" / "trustlens.db"),
)
AUDIT_PATH = os.environ.get("TRUSTLENS_AUDIT")  # if set, every query is logged here

mcp = FastMCP("trustlens-data")


def _audit(action: str, detail: str, outcome: str) -> None:
    """Record a data action to the audit file if TRUSTLENS_AUDIT is configured."""
    if AUDIT_PATH:
        audit_append(AUDIT_PATH, "analyst", action, detail, outcome)


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
    outcome = "ok"
    try:
        check_query(sql)
        rows = db.read_query(DB_PATH, sql).to_dict(orient="records")
        result = json.dumps({"rows": rows})
    except SecurityError as e:
        outcome = "blocked"
        result = json.dumps({"error": f"blocked: {e}"})
    except Exception as e:  # malformed SQL, missing table, etc.
        outcome = "error"
        result = json.dumps({"error": str(e)})
    _audit("query_data", sql, outcome)
    return result


if __name__ == "__main__":
    mcp.run(transport="stdio")
