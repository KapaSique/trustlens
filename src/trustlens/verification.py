"""Deterministic verification of numeric claims — the TrustLens differentiator.

Instead of asking an LLM to re-check its own work (weaker and still
hallucination-prone), the Verifier RE-EXECUTES the underlying query and compares
the actual scalar result to the claimed value. A mismatch beyond tolerance is a
caught hallucination — proven with a number, not a second opinion.
"""

from trustlens import db
from trustlens.security import SecurityError, check_query


def verify_numeric_claim(
    db_path: str, sql: str, claimed: float, tol: float = 0.01
) -> dict:
    """Re-run `sql` and check its scalar result against `claimed`.

    Returns a dict with `verified` (bool) plus `actual`/`claimed`, or an
    `error` if the query is unsafe, fails, or yields no scalar.
    """
    try:
        check_query(sql)
    except SecurityError as e:
        return {"verified": False, "error": f"blocked: {e}", "claimed": claimed}
    try:
        frame = db.read_query(db_path, sql)
    except Exception as e:  # malformed SQL, missing table, etc.
        return {"verified": False, "error": str(e), "claimed": claimed}
    if frame.empty or frame.shape[1] < 1:
        return {"verified": False, "error": "query returned no scalar", "claimed": claimed}

    actual = frame.iloc[0, 0]
    try:
        actual_f = float(actual)
        claimed_f = float(claimed)
    except (TypeError, ValueError):
        # non-numeric claim: fall back to exact string comparison
        verified = str(actual) == str(claimed)
        return {"verified": verified, "actual": actual, "claimed": claimed}

    return {
        "verified": abs(actual_f - claimed_f) <= tol,
        "actual": actual_f,
        "claimed": claimed_f,
    }
