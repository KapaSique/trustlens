"""Query policy guard for TrustLens.

Enforces: read-only (SELECT only), single statement, no PII columns.
This is the security concept for the capstone — every data access is gated
before it reaches the database.
"""


class SecurityError(Exception):
    """Raised when a query violates the access policy."""


# Columns that identify individuals — never exposed in insights.
PII_COLUMNS = {
    "customer_id",
    "customer_unique_id",
    "seller_id",
    "customer_zip_code_prefix",
}

_BLOCKED_KEYWORDS = ("drop", "delete", "update", "insert", "alter", "create", "pragma")


def check_query(sql: str) -> None:
    """Raise SecurityError if the query is not a safe, read-only SELECT."""
    stripped = sql.strip().rstrip(";")
    if ";" in stripped:
        raise SecurityError("multiple statements are not allowed")
    if not stripped.lower().startswith("select"):
        raise SecurityError("only SELECT queries are allowed")
    lowered = stripped.lower()
    padded = f" {lowered} "
    for kw in _BLOCKED_KEYWORDS:
        if f" {kw} " in padded:
            raise SecurityError(f"keyword '{kw}' is not allowed")
    for pii in PII_COLUMNS:
        if pii in lowered:
            raise SecurityError(f"column '{pii}' is PII and cannot be queried")
