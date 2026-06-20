import json

from trustlens.audit import AuditLog, audit_append, load_audit


def test_audit_records_entries():
    log = AuditLog()
    log.record("analyst", "query_data", "SELECT 1", "ok")
    log.record("security", "query_data", "DROP TABLE orders", "blocked")
    assert len(log) == 2
    entries = log.entries()
    assert entries[0].actor == "analyst"
    assert entries[1].outcome == "blocked"


def test_audit_to_json_is_serializable():
    log = AuditLog()
    log.record("verifier", "verify", "claim=70", "ok")
    data = json.loads(log.to_json())
    assert data[0]["action"] == "verify"
    assert data[0]["actor"] == "verifier"
    assert "ts" in data[0]


def test_audit_summary_counts_outcomes():
    log = AuditLog()
    log.record("analyst", "query_data", "SELECT 1", "ok")
    log.record("verifier", "verify", "claim=5", "mismatch")
    log.record("security", "query_data", "DELETE x", "blocked")
    summary = log.summary()
    assert summary["ok"] == 1
    assert summary["mismatch"] == 1
    assert summary["blocked"] == 1


def test_audit_append_and_load_roundtrip(tmp_path):
    path = str(tmp_path / "audit.jsonl")
    audit_append(path, "analyst", "query_data", "SELECT 1", "ok")
    audit_append(path, "security", "query_data", "DROP TABLE x", "blocked")
    log = load_audit(path)
    assert len(log) == 2
    assert log.entries()[0].actor == "analyst"
    assert log.entries()[1].outcome == "blocked"
    assert log.summary() == {"ok": 1, "blocked": 1}
