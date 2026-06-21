"""Planner agent: decomposes a business question into ordered analysis steps."""

from google.adk.agents import LlmAgent

from trustlens.model_config import MODEL, resilient_config

INSTRUCTION = (
    "You are an analytics planner for an e-commerce business. "
    "Given a business question, break it into a short ordered list of concrete "
    "data-analysis steps (which tables and metrics to look at). "
    "Be specific and minimal — only the steps needed to answer the question."
)


def build_planner() -> LlmAgent:
    """Construct the Planner agent. Saves its plan to state['plan']."""
    return LlmAgent(
        model=MODEL,
        name="planner",
        instruction=INSTRUCTION,
        output_key="plan",
        generate_content_config=resilient_config(),
    )
