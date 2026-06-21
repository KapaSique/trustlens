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


def test_allows_cte():
    check_query("WITH t AS (SELECT price FROM order_items) SELECT SUM(price) FROM t")


def test_blocks_cte_with_mutation():
    with pytest.raises(SecurityError):
        check_query("WITH t AS (SELECT 1) DELETE FROM orders")


def test_blocks_attach():
    with pytest.raises(SecurityError):
        check_query("ATTACH DATABASE 'evil.db' AS e")


def test_pii_substring_in_alias_allowed():
    # an alias that merely CONTAINS a PII substring must not trip the gate
    check_query("SELECT AVG(price) AS avg_price_no_seller_idx FROM order_items")
    check_query("SELECT COUNT(*) AS orders_by_customer_idx FROM orders")
