import sqlite3

from trustlens.verification import verify_numeric_claim


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


def test_verify_confirms_correct_claim(tmp_path):
    path = _seed(tmp_path)
    out = verify_numeric_claim(path, "SELECT SUM(price) FROM orders WHERE region='SP'", 70.0)
    assert out["verified"] is True
    assert out["actual"] == 70.0


def test_verify_catches_hallucination(tmp_path):
    path = _seed(tmp_path)
    out = verify_numeric_claim(path, "SELECT SUM(price) FROM orders WHERE region='SP'", 999.0)
    assert out["verified"] is False
    assert out["actual"] == 70.0


def test_verify_rejects_unsafe_sql(tmp_path):
    path = _seed(tmp_path)
    out = verify_numeric_claim(path, "DROP TABLE orders", 0)
    assert out["verified"] is False
    assert "error" in out


def test_verify_within_tolerance(tmp_path):
    path = _seed(tmp_path)
    out = verify_numeric_claim(path, "SELECT SUM(price) FROM orders WHERE region='SP'", 70.005)
    assert out["verified"] is True
