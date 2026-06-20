"""Run the Analyst agent on a single question and print the final answer.

Usage:
  uv run python src/trustlens/run_analyst.py "Which region has the highest revenue?"
Requires GEMINI_API_KEY in the environment (or a .env file).
"""

import asyncio
import sys

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from trustlens.agents.analyst import build_analyst


async def answer(question: str) -> str:
    """Run the Analyst agent on one question and return its final text answer."""
    agent, toolset = build_analyst()
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        state={}, app_name="trustlens", user_id="u1"
    )
    runner = Runner(
        app_name="trustlens", agent=agent, session_service=session_service
    )
    content = types.Content(role="user", parts=[types.Part(text=question)])
    final = ""
    try:
        async for event in runner.run_async(
            session_id=session.id, user_id=session.user_id, new_message=content
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        final = part.text
    finally:
        await toolset.close()
    return final


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "Which region has the highest revenue?"
    print(asyncio.run(answer(q)))
