"""Verifier agent: independently re-checks each numeric claim from the analyst.

The verification itself is deterministic (re-executes the SQL); the agent's job
is to call the verify_claim tool for every figure and summarize what survived.
"""

import json
import os
from pathlib import Path

from google.adk.agents import LlmAgent

from trustlens.model_config import MODEL, resilient_config
from trustlens.verification import verify_numeric_claim

DB_PATH = os.environ.get(
    "TRUSTLENS_DB",
    # this file is src/trustlens/agents/verifier.py -> parents[3] is the repo root
    str(Path(__file__).resolve().parents[3] / "data" / "trustlens.db"),
)


def verify_claim(sql: str, claimed_value: float) -> str:
    """Re-execute the SQL behind a claimed figure and check it against the value.

    Returns JSON {"verified": bool, "actual": ..., "claimed": ...} or {"error": ...}.
    Call this for EVERY number before it is reported.
    """
    return json.dumps(verify_numeric_claim(DB_PATH, sql, claimed_value))


INSTRUCTION = (
    "You are a verification agent. The analyst's findings are in {findings}, each with "
    "the SQL that produced it and the claimed figure. For EVERY claimed figure, call "
    "verify_claim with its SQL and value. Summarize which figures were verified and "
    "which were rejected (mismatch or error). Never accept a number you did not verify."
)


def build_verifier() -> LlmAgent:
    """Construct the Verifier agent. Saves its summary to state['verification']."""
    return LlmAgent(
        model=MODEL,
        name="verifier",
        instruction=INSTRUCTION,
        tools=[verify_claim],
        output_key="verification",
        generate_content_config=resilient_config(),
    )
