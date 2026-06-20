"""Reporter agent: turns verified findings into a concise business report."""

from google.adk.agents import LlmAgent

INSTRUCTION = (
    "You are a business analyst writing the final report. "
    "You are given the analyst findings in {findings} and the verification results "
    "in {verification}. Report ONLY figures whose verification confirmed them. "
    "For any figure the verifier flagged as unverified or mismatched, explicitly state "
    "it was rejected and do NOT present it as fact. Be concise and decision-oriented."
)


def build_reporter() -> LlmAgent:
    """Construct the Reporter agent. Saves its report to state['report']."""
    return LlmAgent(
        model="gemini-flash-latest",
        name="reporter",
        instruction=INSTRUCTION,
        output_key="report",
    )
