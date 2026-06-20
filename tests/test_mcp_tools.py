import sqlite3

import pandas as pd

from trustlens import db


def _seed(tmp_path):
    p = tmp_path / "t.db"
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE orders (order_id TEXT, price REAL, region TEXT)")
    con.executemany(
        "INSERT INTO orders VALUES (?,?,?)",
        [("a", 10.0, "SP"), ("b", 30.0, "RJ"), ("c", 60.0, "SP")],
    )
    con.commit()
    con.close()
    return str(p)


def test_get_schema_lists_tables_and_columns(tmp_path):
    path = _seed(tmp_path)
    schema = db.get_schema(path)
    assert "orders" in schema
    assert "price" in schema["orders"]


def test_read_query_returns_dataframe(tmp_path):
    path = _seed(tmp_path)
    out = db.read_query(path, "SELECT region, SUM(price) AS total FROM orders GROUP BY region")
    assert isinstance(out, pd.DataFrame)
    assert out.set_index("region").loc["SP", "total"] == 70.0
