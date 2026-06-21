"""Demo: the deterministic Verifier catches a hallucinated figure.

Runs WITHOUT an LLM / API key. Uses the real Olist db if it has been built,
otherwise falls back to a tiny synthetic db so it works on a fresh clone with
zero downloads.

  uv run python examples/demo_verifier.py
"""

import tempfile
from pathlib import Path

from trustlens import db
from trustlens.sample_data import build_sample_db
from trustlens.verification import verify_numeric_claim

REAL_DB = Path(__file__).resolve().parents[1] / "data" / "trustlens.db"


def _resolve_db() -> tuple[str, str]:
    if REAL_DB.exists():
        return str(REAL_DB), "real Olist dataset"
    tmp = str(Path(tempfile.gettempdir()) / "trustlens_sample.db")
    build_sample_db(tmp)
    return tmp, "synthetic sample (no download needed)"


def main() -> None:
    db_path, source = _resolve_db()
    print(f"data source: {source}\n")

    top = db.read_query(
        db_path,
        "SELECT p.product_category_name AS cat, SUM(oi.price) AS rev "
        "FROM order_items oi JOIN products p ON oi.product_id = p.product_id "
        "GROUP BY cat ORDER BY rev DESC LIMIT 1",
    )
    cat = top.iloc[0, 0]
    rev = float(top.iloc[0, 1])
    scalar_sql = (
        "SELECT SUM(oi.price) FROM order_items oi "
        "JOIN products p ON oi.product_id = p.product_id "
        f"WHERE p.product_category_name = '{cat}'"
    )

    print(f"Top category by revenue: {cat}  (true revenue: {rev:,.2f})\n")

    honest = verify_numeric_claim(db_path, scalar_sql, rev)
    print(
        f"[honest claim]       analyst says {rev:,.2f} "
        f"-> verified={honest['verified']}  (actual {honest['actual']:,.2f})"
    )

    fake = round(rev * 1.18, 2)  # an inflated, hallucinated figure
    caught = verify_numeric_claim(db_path, scalar_sql, fake)
    print(
        f"[hallucinated claim] analyst says {fake:,.2f} "
        f"-> verified={caught['verified']}  (actual {caught['actual']:,.2f})"
    )

    print("\n=> TrustLens rejects the hallucinated figure before it reaches the report.")


if __name__ == "__main__":
    main()
