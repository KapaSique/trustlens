from trustlens import db
from trustlens.sample_data import build_sample_db


def test_sample_db_has_three_tables(tmp_path):
    p = str(tmp_path / "s.db")
    build_sample_db(p)
    schema = db.get_schema(p)
    assert set(schema) == {"orders", "order_items", "products"}


def test_sample_db_revenue_is_known(tmp_path):
    p = str(tmp_path / "s.db")
    build_sample_db(p)
    out = db.read_query(p, "SELECT SUM(price) AS r FROM order_items")
    assert out.iloc[0, 0] == 500.0  # 100 + 200 + 50 + 150
