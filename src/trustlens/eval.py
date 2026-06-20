"""Evaluate the deterministic verifier on a set of business questions.

build_eval_set validates raw {question, sql} candidates against the real database
(keeping only those that pass the security gate and return one numeric scalar) and
records the ground-truth value. evaluate_verifier then checks, for every item, that
the verifier confirms the true value and catches an inflated (hallucinated) one.

No LLM / API quota needed — the verification is deterministic.
"""

import html

from trustlens import db
from trustlens.security import SecurityError, check_query
from trustlens.verification import verify_numeric_claim


def build_eval_set(db_path: str, raw_questions: list[dict]) -> list[dict]:
    """Validate {question, sql} items; keep those that yield one numeric scalar.

    Returns [{question, sql, truth}] with HTML-unescaped, security-passing SQL.
    """
    out: list[dict] = []
    for q in raw_questions:
        sql = html.unescape(q["sql"]).strip().rstrip(";")
        try:
            check_query(sql)
            frame = db.read_query(db_path, sql)
        except (SecurityError, Exception):
            continue
        if frame.shape[0] != 1 or frame.shape[1] != 1:
            continue
        try:
            truth = float(frame.iloc[0, 0])
        except (TypeError, ValueError):
            continue
        out.append({"question": q["question"], "sql": sql, "truth": truth})
    return out


def evaluate_verifier(db_path: str, eval_set: list[dict], inflate: float = 1.15) -> dict:
    """Check the verifier confirms each true value and catches an inflated one.

    Returns counts and rates: confirmed_rate (no false rejects) and catch_rate
    (hallucinations caught).
    """
    n = len(eval_set)
    confirmed = 0
    caught = 0
    for item in eval_set:
        sql, truth = item["sql"], item["truth"]
        honest = verify_numeric_claim(db_path, sql, truth)
        if honest.get("verified"):
            confirmed += 1
        fake = truth * inflate if truth else 1.0
        hallucinated = verify_numeric_claim(db_path, sql, fake)
        if hallucinated.get("verified") is False:
            caught += 1
    return {
        "n": n,
        "confirmed": confirmed,
        "caught": caught,
        "confirmed_rate": confirmed / n if n else 0.0,
        "catch_rate": caught / n if n else 0.0,
    }
