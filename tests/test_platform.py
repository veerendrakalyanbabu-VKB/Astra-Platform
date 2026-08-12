import pytest

from astra.core.knowledge import KnowledgeEngine
from astra.core.tools import ToolManager, register_builtin_tools
from astra.core.safety import SafetyEngine
from astra.core.bus import EventBus
from astra.core.observability import MetricsCollector
from astra.core.planner.plan import Plan


def test_knowledge_search(tmp_path):
    engine = KnowledgeEngine()
    results = engine.search("astra")

    assert len(results) > 0
    assert "AI-native" in results[0]["content"]


def test_knowledge_best_match():
    engine = KnowledgeEngine()
    answer = engine.best_match("tell me about memory")

    assert answer is not None
    assert "remember" in answer.lower()


def test_tool_calculator():
    tools = ToolManager()
    register_builtin_tools(tools)

    result = tools.invoke("calculator", {"expression": "15 * 7"})

    assert result["success"] is True
    assert result["result"]["result"] == 105


def test_safety_blocks_critical():
    safety = SafetyEngine()
    plan = Plan(action="FORMAT_DISK", parameters={"drive": "C:"})
    result = safety.evaluate(plan, "EXECUTE")

    assert result["decision"] == "BLOCK"


def test_safety_session_limit():
    safety = SafetyEngine()
    plan = Plan(action="DELETE_FILE", parameters={"target": "a.txt"})

    for _ in range(5):
        safety.record_execution("DELETE_FILE")

    result = safety.evaluate(plan, "CONFIRM")

    assert result["decision"] == "BLOCK"
    assert "limit" in result["message"].lower()


def test_event_bus():
    bus = EventBus()
    received = []

    bus.subscribe("test.event", lambda payload: received.append(payload))
    bus.publish("test.event", {"value": 42})

    assert received[0]["value"] == 42


def test_metrics():
    metrics = MetricsCollector()
    metrics.increment("requests")
    metrics.increment("requests")
    metrics.record_timing("pipeline", 12.5)

    snapshot = metrics.snapshot()

    assert snapshot["counters"]["requests"] == 2
    assert snapshot["timings"]["pipeline"]["count"] == 1
