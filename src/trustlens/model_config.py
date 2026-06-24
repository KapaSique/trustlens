"""Shared model configuration for all agents.

The Gemini free tier allows only 5 requests/min, and a full 4-agent run exceeds
that, so every agent retries 429 RESOURCE_EXHAUSTED with exponential backoff
instead of crashing. This keeps the pipeline runnable on the free tier (just
slower) and is good practice on any tier.
"""

import os

from google.genai import types

# Override with TRUSTLENS_MODEL when the default is overloaded (503) or rate-limited.
MODEL = os.environ.get("TRUSTLENS_MODEL", "gemini-flash-latest")


def resilient_config() -> types.GenerateContentConfig:
    """GenerateContentConfig with 429/503-aware retry and exponential backoff."""
    return types.GenerateContentConfig(
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(
                attempts=6,
                initial_delay=8,
                exp_base=2,
                http_status_codes=[429, 503],
            ),
        ),
    )
