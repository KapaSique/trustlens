import os

import pytest

from trustlens.run_analyst import answer


@pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY"), reason="needs GEMINI_API_KEY"
)
@pytest.mark.asyncio
async def test_analyst_answers_with_a_number():
    out = await answer("Which order region has the highest total revenue?")
    assert any(ch.isdigit() for ch in out)
