# TrustLens — the Insights Agent you can actually trust

> A multi-agent business-intelligence system that **re-verifies every number before it shows it** — because hallucinating AI analytics can't be trusted with business decisions.

**Capstone — 5-Day AI Agents Intensive (Google × Kaggle) · Track: Agents for Business**

---

## The problem

Enterprises are drowning in data, and "chat with your data" LLM tools promise instant answers. But they **hallucinate figures** — confidently reporting a revenue number that isn't in the data. One wrong number in a board deck is worse than no answer at all, so teams can't trust these tools for real decisions. That trust gap is the actual blocker to AI adoption in business analytics.

## The solution

TrustLens is a four-agent pipeline where an independent **Verifier** re-checks every figure against the source data before it reaches the report. Its verification is **deterministic** — it re-executes the query and compares the result to the claimed value — so a hallucination is caught with a number, not a second opinion.

```
   Business question (natural language)
            │
   ┌────────▼────────┐
   │     Planner     │  decomposes the question into analysis steps      → state["plan"]
   └────────┬────────┘
   ┌────────▼────────┐
   │     Analyst     │  queries the data via MCP tools (get_schema,      → state["findings"]
   │                 │  query_data), returns figures + the SQL behind them
   └────────┬────────┘
   ┌────────▼────────┐
   │   Verifier ★    │  re-executes each figure's SQL and compares to    → state["verification"]
   │                 │  the claim — flags any mismatch as a hallucination
   └────────┬────────┘
   ┌────────▼────────┐
   │    Reporter     │  writes the report using ONLY verified figures    → state["report"]
   └────────┬────────┘
            │
   Verified business insight  +  audit trail
```

Every data access passes a **security gate** (read-only, no PII, single statement) and is recorded in an **audit log**.

## Course concepts demonstrated (4 of the required ≥3)

| Concept | Where |
|---|---|
| **Multi-agent (ADK)** | `SequentialAgent` orchestrating Planner / Analyst / Verifier / Reporter (`src/trustlens/pipeline.py`) |
| **MCP servers** | `src/trustlens/mcp_server.py` — a FastMCP server exposing `get_schema` and `query_data`, consumed by the Analyst via `McpToolset` over stdio |
| **Agent skills / tools** | the Verifier's `verify_claim` tool; analytical querying as agent tools |
| **Security** | `src/trustlens/security.py` (SELECT-only + PII gate), verification-as-trust-gate, `src/trustlens/audit.py` audit trail, secrets via `.env` (no keys in code) |

## The differentiator: deterministic verification

Most "self-checking" agents just ask the LLM again — which can hallucinate again. TrustLens re-runs the actual query:

```text
Top category by revenue: beleza_saude  (true revenue: 1,258,681.34)

[honest claim]       analyst says 1,258,681.34 -> verified=True   (actual 1,258,681.34)
[hallucinated claim] analyst says 1,485,243.98 -> verified=False  (actual 1,258,681.34)

=> TrustLens rejects the hallucinated figure before it reaches the report.
```

Reproduce it (no API key needed): `uv run python examples/demo_verifier.py`

## Setup

Requires [uv](https://docs.astral.sh/uv/), Python 3.12, and a Gemini API key.

```bash
# 1. install dependencies
uv sync

# 2. get the data (Olist Brazilian e-commerce, 3 core tables)
kaggle datasets download -d olistbr/brazilian-ecommerce -p data/raw --unzip
uv run python data/load_olist.py        # builds data/trustlens.db

# 3. add your Gemini key
cp .env.example .env                     # then edit: GEMINI_API_KEY=...
```

## Run

```bash
# single Analyst (foundation)
uv run python src/trustlens/run_analyst.py "Which order status is most common?"

# full Planner -> Analyst -> Verifier -> Reporter pipeline
uv run python src/trustlens/pipeline.py "What are the top 3 product categories by revenue?"

# deterministic verifier demo (no key needed)
uv run python examples/demo_verifier.py
```

> **Note on Gemini free tier:** `gemini-flash-latest` resolves to `gemini-3.5-flash`, limited to **5 requests/min and 20/day** on the free tier. A full 4-agent run uses ~8–15 calls, so use a paid tier (or run on Kaggle/Vertex) for repeated runs.

## Project structure

```
src/trustlens/
  db.py            # read-only SQLite access (?mode=ro)
  security.py      # query policy gate: SELECT-only, single-statement, PII block
  mcp_server.py    # FastMCP data server (get_schema, query_data)
  verification.py  # deterministic numeric verifier (the differentiator)
  audit.py         # append-only action audit log
  agents/
    planner.py     # decompose question -> plan
    analyst.py     # query data via MCP -> findings
    verifier.py    # re-check each figure -> verification
    reporter.py    # verified-only report
  pipeline.py      # SequentialAgent wiring + run_pipeline()
  run_analyst.py   # single-agent entrypoint
data/load_olist.py # build the SQLite db from Olist CSVs
examples/demo_verifier.py
tests/             # 22 unit + construct tests
```

## Testing

```bash
uv run pytest -k "not smoke"   # 22 unit/construct tests, no API key needed
uv run pytest                  # includes the live smoke test (needs GEMINI_API_KEY + quota)
uv run ruff check src tests    # lint
```

## Security notes

- The database is opened **read-only**; the security gate blocks any non-SELECT, multi-statement, or PII-column query before execution.
- No API keys in code — `GEMINI_API_KEY` is loaded from `.env` (git-ignored).
- Every data action is recorded in the audit log for traceability.
