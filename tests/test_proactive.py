from astra.core.planner.proactive import ProactiveEngine


def test_proactive_suggestions():
    engine = ProactiveEngine()
    suggestions = engine.suggest(limit=3)

    assert len(suggestions) <= 3
    assert all("command" in item for item in suggestions)
