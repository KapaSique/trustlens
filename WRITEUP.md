# TrustLens — the Insights Agent you can actually trust

*Capstone writeup · 5-Day AI Agents Intensive (Google × Kaggle) · Track: Agents for Business*

## The problem worth solving

Every enterprise wants to ask its data questions in plain English and get an answer. The technology is here — but adoption isn't, and the reason is **trust**. LLM analytics tools hallucinate figures: they'll confidently report "Q3 revenue was $4.2M" when the real number is $3.6M, and nothing in the answer signals which is which. In analytics, a confidently-wrong number is worse than no answer — it ends up in a decision. Until a business can trust the figure, it can't ship the agent.

## Why agents — and why *multiple* agents

A single LLM that both computes and reports a number has no incentive or mechanism to catch its own mistake. The fix mirrors how humans build trust in numbers: **separation of duties**. One party produces the figure; an *independent* party verifies it against the source before it's published. That maps naturally onto a multi-agent system:

- **Planner** — turns a business question into concrete analysis steps.
- **Analyst** — queries the data and reports figures *with the SQL that produced them*.
- **Verifier** — independently re-checks every figure.
- **Reporter** — publishes only what survived verification.

## The key insight: verify deterministically, not with a second opinion

Most "self-correcting" agents ask the LLM to double-check itself — but the same model that hallucinated can hallucinate the check. TrustLens's Verifier doesn't ask; it **re-executes the query** and compares the actual scalar result to the claimed value. A mismatch beyond tolerance is a caught hallucination, proven by a number. This is the project's core idea, and it's the difference between "probably right" and "verified."

## Proof it works

On the real Olist e-commerce dataset (~99k orders, ~113k order items), with no LLM involved in the check:

```
Top category by revenue: beleza_saude  (true revenue: 1,258,681.34)
[honest claim]       1,258,681.34 -> verified=True
[hallucinated claim] 1,485,243.98 -> verified=False  (actual 1,258,681.34)
```

The Verifier catches an inflated figure before it reaches the report. The full system is covered by 22 unit and integration tests, and the single-agent path was confirmed end-to-end against live Gemini (the agent answered "delivered — 96,478 orders," pulling the figure through the MCP tools, not inventing it).

## Architecture in one paragraph

A Google ADK `SequentialAgent` chains the four agents, each passing its output to the next through session state. The Analyst reaches the data only through an **MCP server** (FastMCP) exposing `get_schema` and `query_data`, and every query passes a **security gate** — read-only, single-statement, no PII columns — before it runs. The Verifier calls a deterministic `verify_claim` tool. An append-only **audit log** records every action. Four of the course's key concepts — multi-agent (ADK), MCP, agent tools/skills, and security — are each load-bearing, not decorative.

## The journey

The project went from idea to working system through a disciplined path: a brainstorm to pick the Business-track angle, a rubric-driven spec (the rubric *is* the metric for a judged hackathon), then test-driven implementation in small committed steps. The most honest lesson came from the Gemini free tier: a 4-agent run burns ~8–15 LLM calls and the free tier allows only 20/day, which is why the deterministic verifier — testable and demonstrable **without** burning quota — became both the technical centerpiece and the reliable demo.

## Impact and what's next

TrustLens turns "AI gave me a number" into "AI gave me a *verified* number, and here's the audit trail." That's the missing ingredient for putting analytics agents in front of real business decisions. Natural extensions: live database connectors, per-figure confidence scoring, and a reviewer dashboard over the audit log.

---

*Code, setup, and the reproducible verifier demo are in the repository README.*
