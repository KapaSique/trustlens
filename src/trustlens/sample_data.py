"""Build a tiny synthetic Olist-shaped database.

Lets the demo and eval run with zero external downloads (no Kaggle CLI, no key),
so a judge can reproduce the verifier in seconds. The numbers are deliberately
small and known, not representative of the real dataset.
"""

import sqlite3

_ORDERS = [
    ("o1", "c1", "delivered", "2018-01-15"),
    ("o2", "c2", "delivered", "2018-02-20"),
    ("o3", "c3", "canceled", "2017-03-10"),
    ("o4", "c4", "delivered", "2017-07-01"),
]
_ITEMS = [
    ("o1", "p1", 100.0, 10.0),
    ("o2", "p2", 200.0, 25.0),
    ("o3", "p1", 50.0, 5.0),
    ("o4", "p1", 150.0, 15.0),
]
_PRODUCTS = [
    ("p1", "beleza_saude"),
    ("p2", "cama_mesa_banho"),
]


def build_sample_db(path: str) -> None:
    """Create a fresh 3-table synthetic db at path (orders, order_items, products)."""
    con = sqlite3.connect(path)
    try:
        con.execute(
            "CREATE TABLE orders "
            "(order_id TEXT, customer_id TEXT, order_status TEXT, order_purchase_timestamp TEXT)"
        )
        con.execute(
            "CREATE TABLE order_items "
            "(order_id TEXT, product_id TEXT, price REAL, freight_value REAL)"
        )
        con.execute("CREATE TABLE products (product_id TEXT, product_category_name TEXT)")
        con.executemany("INSERT INTO orders VALUES (?,?,?,?)", _ORDERS)
        con.executemany("INSERT INTO order_items VALUES (?,?,?,?)", _ITEMS)
        con.executemany("INSERT INTO products VALUES (?,?)", _PRODUCTS)
        con.commit()
    finally:
        con.close()
