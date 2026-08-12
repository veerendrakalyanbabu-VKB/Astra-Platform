from astra.core.planner.plan import Plan
from astra.core.reasoning import ReasoningEngine


def test_low_risk_executes():
    engine = ReasoningEngine()
    plan = Plan(action="OPEN_APP", parameters={"application": "notepad"})
    result = engine.think(plan)

    assert result["analysis"]["risk"] == "LOW"
    assert result["decision"]["decision"] == "EXECUTE"


def test_high_risk_requires_confirm():
    engine = ReasoningEngine()
    plan = Plan(action="DELETE_FILE", parameters={"target": "notes.txt"})
    result = engine.think(plan)

    assert result["analysis"]["risk"] == "HIGH"
    assert result["decision"]["decision"] == "CONFIRM"


def test_critical_risk_blocked():
    engine = ReasoningEngine()
    plan = Plan(action="FORMAT_DISK", parameters={"drive": "C:"})
    result = engine.think(plan)

    assert result["analysis"]["risk"] == "CRITICAL"
    assert result["decision"]["decision"] == "BLOCK"
