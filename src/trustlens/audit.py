"""Append-only audit log of agent and data actions.

Every data access, verification, and security decision is recorded so a judge
(or an auditor) can trace exactly what the agents did and why an insight was
accepted or rejected. This is the observability half of the security story.
"""

import json
import time
from dataclasses import asdict, dataclass


@dataclass
class AuditEntry:
    actor: str  # which agent/component acted (analyst, verifier, security)
    action: str  # what it did (query_data, verify, ...)
    detail: str  # the SQL, claim, or payload
    outcome: str  # ok / blocked / mismatch / error
    ts: float  # unix timestamp


class AuditLog:
    """In-memory, append-only record of actions taken during a run."""

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    def record(self, actor: str, action: str, detail: str, outcome: str) -> None:
        """Append one action to the log."""
        self._entries.append(AuditEntry(actor, action, detail, outcome, time.time()))

    def entries(self) -> list[AuditEntry]:
        """Return a copy of the recorded entries in order."""
        return list(self._entries)

    def summary(self) -> dict[str, int]:
        """Count entries by outcome (ok / blocked / mismatch / error)."""
        counts: dict[str, int] = {}
        for e in self._entries:
            counts[e.outcome] = counts.get(e.outcome, 0) + 1
        return counts

    def to_json(self) -> str:
        """Serialize the full log as a JSON array."""
        return json.dumps([asdict(e) for e in self._entries], indent=2)

    def __len__(self) -> int:
        return len(self._entries)
