"""Query policy guard for TrustLens.

A defense-in-depth heuristic gate, backed by a read-only (mode=ro) connection in
db.py. It enforces, before any query runs:
  - read-only shape: the statement must start with SELECT or a WITH (CTE) ... SELECT
  - single statement: no ';'-separated second statement
  - no mutating keywords (drop/delete/update/insert/alter/create/pragma/attach)
  - no PII columns referenced

Matching is word-boundary based so aliases that merely contain a PII substring
(e.g. ``revenue_per_seller_group``) are allowed, while a real column reference
(``seller_id``) is blocked. This gate is the first line; the mode=ro connection
guarantees no write can land even if a statement slipped past it.
"""

import re


class SecurityError(Exception):
    """Raised when a query violates the access policy."""


# Columns that identify individuals — never exposed in insights.
PII_COLUMNS = {
    "customer_id",
    "customer_unique_id",
    "seller_id",
    "customer_zip_code_prefix",
}

_BLOCKED_KEYWORDS = (
    "drop",
    "delete",
    "update",
    "insert",
    "alter",
    "create",
    "pragma",
    "attach",
)


def check_query(sql: str) -> None:
    """Raise SecurityError if the query is not a safe, read-only SELECT/CTE."""
    stripped = sql.strip().rstrip(";")
    if ";" in stripped:
        raise SecurityError("multiple statements are not allowed")
    low = stripped.lower()
    if not (low.startswith("select") or low.startswith("with")):
        raise SecurityError("only read-only SELECT or WITH ... SELECT queries are allowed")
    for kw in _BLOCKED_KEYWORDS:
        if re.search(rf"\b{kw}\b", low):
            raise SecurityError(f"keyword '{kw}' is not allowed")
    for pii in PII_COLUMNS:
        if re.search(rf"\b{pii}\b", low):
            raise SecurityError(f"column '{pii}' is PII and cannot be queried")
