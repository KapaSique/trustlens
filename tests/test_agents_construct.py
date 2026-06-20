import asyncio
import json
import sqlite3

import trustlens.agents.verifier as verifier_mod
from trustlens.agents.analyst import build_analyst
from trustlens.agents.planner import build_planner
from trustlens.agents.reporter import build_reporter
from trustlens.agents.verifier import build_verifier


def test_planner_constructs():
    a = build_planner()
    assert a.name == "planner"
    assert a.output_key == "plan"


def test_reporter_constructs():
    a = build_reporter()
    assert a.name == "reporter"
    assert a.output_key == "report"


def test_verifier_constructs_with_tool():
    a = build_verifier()
    assert a.name == "verifier"
    assert a.output_key == "verification"
    assert len(a.tools) == 1


def test_analyst_accepts_output_key():
    a, toolset = build_analyst(output_key="findings")
    assert a.output_key == "findings"
    asyncio.run(toolset.close())


def test_verify_claim_tool_confirms_and_catches(tmp_path, monkeypatch):
    p = tmp_path / "t.db"
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE orders (price REAL)")
    con.executemany("INSERT INTO orders VALUES (?)", [(10.0,), (60.0,)])
    con.commit()
    con.close()
    monkeypatch.setattr(verifier_mod, "DB_PATH", str(p))

    ok = json.loads(verifier_mod.verify_claim("SELECT SUM(price) FROM orders", 70.0))
    assert ok["verified"] is True
    bad = json.loads(verifier_mod.verify_claim("SELECT SUM(price) FROM orders", 999.0))
    assert bad["verified"] is False
