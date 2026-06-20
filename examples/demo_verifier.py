"""Demo: the deterministic Verifier catches a hallucinated figure on real Olist data.

Runs WITHOUT an LLM / API key — pure, reproducible data verification. This is the
core of the TrustLens differentiator, shown as a number.

  uv run python examples/demo_verifier.py
"""

from pathlib import Path

from trustlens import db
from trustlens.verification import verify_numeric_claim

DB = str(Path(__file__).resolve().parents[1] / "data" / "trustlens.db")


def main() -> None:
    # Find the real top product category by revenue (ground truth from the data).
    top = db.read_query(
        DB,
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

    honest = verify_numeric_claim(DB, scalar_sql, rev)
    print(
        f"[honest claim]       analyst says {rev:,.2f} "
        f"-> verified={honest['verified']}  (actual {honest['actual']:,.2f})"
    )

    fake = round(rev * 1.18, 2)  # an inflated, hallucinated figure
    caught = verify_numeric_claim(DB, scalar_sql, fake)
    print(
        f"[hallucinated claim] analyst says {fake:,.2f} "
        f"-> verified={caught['verified']}  (actual {caught['actual']:,.2f})"
    )

    print("\n=> TrustLens rejects the hallucinated figure before it reaches the report.")


if __name__ == "__main__":
    main()
