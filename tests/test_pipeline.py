import asyncio

from trustlens.pipeline import build_pipeline


def test_pipeline_constructs_in_order():
    pipeline, toolset = build_pipeline()
    try:
        assert pipeline.name == "trustlens"
        names = [a.name for a in pipeline.sub_agents]
        assert names == ["planner", "analyst", "verifier", "reporter"]
    finally:
        asyncio.run(toolset.close())
