import pytest

from trustlens.security import SecurityError, check_query


def test_allows_plain_select():
    check_query("SELECT region, SUM(price) FROM order_items GROUP BY region")


def test_blocks_mutation():
    for bad in [
        "DROP TABLE orders",
        "DELETE FROM orders",
        "UPDATE orders SET price=0",
        "INSERT INTO orders VALUES (1)",
    ]:
        with pytest.raises(SecurityError):
            check_query(bad)


def test_blocks_multiple_statements():
    with pytest.raises(SecurityError):
        check_query("SELECT 1; DROP TABLE orders")


def test_blocks_pii_column():
    with pytest.raises(SecurityError):
        check_query("SELECT customer_id FROM orders")
