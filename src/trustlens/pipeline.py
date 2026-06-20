"""TrustLens pipeline: Planner -> Analyst -> Verifier -> Reporter.

A SequentialAgent chains the four agents; each saves its output to session state
(plan / findings / verification / report) for the next one to read.

Usage (needs GEMINI_API_KEY):
  uv run python src/trustlens/pipeline.py "What are the top 3 product categories by revenue?"
"""

import asyncio
import sys

from dotenv import load_dotenv
from google.adk.agents import SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import McpToolset
from google.genai import types

from trustlens.agents.analyst import build_analyst
from trustlens.agents.planner import build_planner
from trustlens.agents.reporter import build_reporter
from trustlens.agents.verifier import build_verifier

load_dotenv()


def build_pipeline() -> tuple[SequentialAgent, McpToolset]:
    """Construct the full Planner->Analyst->Verifier->Reporter pipeline.

    Returns the pipeline agent and the analyst's MCP toolset (close it when done).
    """
    planner = build_planner()
    analyst, toolset = build_analyst(output_key="findings")
    verifier = build_verifier()
    reporter = build_reporter()
    pipeline = SequentialAgent(
        name="trustlens",
        sub_agents=[planner, analyst, verifier, reporter],
    )
    return pipeline, toolset


async def run_pipeline(question: str) -> dict:
    """Run the full pipeline on a question; return the per-stage state."""
    pipeline, toolset = build_pipeline()
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        state={}, app_name="trustlens", user_id="u1"
    )
    runner = Runner(
        app_name="trustlens", agent=pipeline, session_service=session_service
    )
    content = types.Content(role="user", parts=[types.Part(text=question)])
    try:
        async for _event in runner.run_async(
            session_id=session.id, user_id=session.user_id, new_message=content
        ):
            pass
    finally:
        await toolset.close()
    final = await session_service.get_session(
        app_name="trustlens", user_id="u1", session_id=session.id
    )
    state = final.state if final else {}
    return {
        "plan": state.get("plan"),
        "findings": state.get("findings"),
        "verification": state.get("verification"),
        "report": state.get("report"),
    }


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "What are the top 3 product categories by revenue?"
    result = asyncio.run(run_pipeline(q))
    print("=== REPORT ===")
    print(result["report"])
    print("\n=== VERIFICATION ===")
    print(result["verification"])
