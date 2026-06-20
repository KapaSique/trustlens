import sqlite3

from trustlens.eval import build_eval_set, evaluate_verifier


def _seed(tmp_path):
    p = tmp_path / "t.db"
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE order_items (price REAL)")
    con.executemany("INSERT INTO order_items VALUES (?)", [(10.0,), (30.0,), (60.0,)])
    con.commit()
    con.close()
    return str(p)


def test_build_eval_set_keeps_only_valid_scalars(tmp_path):
    path = _seed(tmp_path)
    raw = [
        {"question": "total", "sql": "SELECT SUM(price) FROM order_items"},
        {"question": "blocked", "sql": "DROP TABLE order_items"},
        {"question": "nonscalar", "sql": "SELECT price FROM order_items"},
        {"question": "html", "sql": "SELECT SUM(price) FROM order_items WHERE price &gt; 5"},
    ]
    es = build_eval_set(path, raw)
    questions = {e["question"] for e in es}
    assert questions == {"total", "html"}  # blocked + nonscalar dropped
    truth = {e["question"]: e["truth"] for e in es}
    assert truth["total"] == 100.0


def test_evaluate_verifier_confirms_and_catches(tmp_path):
    path = _seed(tmp_path)
    es = [{"question": "total", "sql": "SELECT SUM(price) FROM order_items", "truth": 100.0}]
    m = evaluate_verifier(path, es)
    assert m["confirmed_rate"] == 1.0
    assert m["catch_rate"] == 1.0
