"""Read-only SQLite access for TrustLens data tools."""

import sqlite3

import pandas as pd


def get_schema(db_path: str) -> dict[str, list[str]]:
    """Return {table_name: [column, ...]} for every table in the database."""
    con = sqlite3.connect(db_path)
    try:
        tables = [
            r[0]
            for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")
        ]
        schema: dict[str, list[str]] = {}
        for t in tables:
            cols = [r[1] for r in con.execute(f"PRAGMA table_info({t})")]
            schema[t] = cols
        return schema
    finally:
        con.close()


def read_query(db_path: str, sql: str) -> pd.DataFrame:
    """Execute a read query and return the result as a DataFrame.

    Opens the connection in read-only mode via URI so writes cannot occur
    even if a mutating statement slips through the upstream security guard.
    """
    uri = f"file:{db_path}?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    try:
        return pd.read_sql_query(sql, con)
    finally:
        con.close()
