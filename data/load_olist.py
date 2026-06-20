"""Build trustlens.db from 3 core Olist tables.

Download once (needs a configured kaggle CLI):
  kaggle datasets download -d olistbr/brazilian-ecommerce -p data/raw --unzip
Then run:
  uv run python data/load_olist.py
"""

import sqlite3
from pathlib import Path

import pandas as pd

RAW = Path(__file__).parent / "raw"
DB = Path(__file__).parent / "trustlens.db"

TABLES = {
    "orders": (
        "olist_orders_dataset.csv",
        ["order_id", "customer_id", "order_status", "order_purchase_timestamp"],
    ),
    "order_items": (
        "olist_order_items_dataset.csv",
        ["order_id", "product_id", "price", "freight_value"],
    ),
    "products": (
        "olist_products_dataset.csv",
        ["product_id", "product_category_name"],
    ),
}


def build() -> None:
    """Load the 3 trimmed tables from data/raw CSVs into a fresh SQLite db."""
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    try:
        for table, (fname, cols) in TABLES.items():
            df = pd.read_csv(RAW / fname, usecols=cols)
            df.to_sql(table, con, index=False)
            print(f"loaded {table}: {len(df)} rows")
    finally:
        con.close()
    print(f"built {DB}")


if __name__ == "__main__":
    build()
