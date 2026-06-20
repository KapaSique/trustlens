"""Build the verifier eval set from candidate questions and report the metric.

Validates each candidate against the real Olist db, then measures whether the
deterministic verifier confirms true values and catches inflated (hallucinated)
ones. Runs WITHOUT an LLM / API key.

  uv run python eval/run_eval.py
"""

import json
from pathlib import Path

from trustlens.eval import build_eval_set, evaluate_verifier

ROOT = Path(__file__).resolve().parents[1]
DB = str(ROOT / "data" / "trustlens.db")
RAW = Path(__file__).parent / "questions_raw.json"
OUT = Path(__file__).parent / "eval_set.json"


def main() -> None:
    raw = json.loads(RAW.read_text())
    eval_set = build_eval_set(DB, raw)
    OUT.write_text(json.dumps(eval_set, indent=2))

    metrics = evaluate_verifier(DB, eval_set)
    print(f"candidates:        {len(raw)}")
    print(f"valid eval items:  {metrics['n']}  (saved to {OUT.name})")
    print(f"confirmed (true accepted):    {metrics['confirmed']}/{metrics['n']} "
          f"= {metrics['confirmed_rate']:.0%}")
    print(f"caught (hallucinations):      {metrics['caught']}/{metrics['n']} "
          f"= {metrics['catch_rate']:.0%}")


if __name__ == "__main__":
    main()
