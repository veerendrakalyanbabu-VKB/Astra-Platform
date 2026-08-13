"""Tests for structured command records."""

from astra.core.intent.models import IntentResult
from astra.core.pipeline.result import PipelineResult
from astra.core.commands.command_record import build_command_record, CommandRecord


def test_command_record_new_id():
    a = CommandRecord.new_id()
    b = CommandRecord.new_id()
    assert len(a) == 12
    assert a != b


def test_build_command_record_success():
    intent = IntentResult(intent="GET_TIME", entities={}, confidence=0.95)
    result = PipelineResult(
        input="what time is it",
        intent=intent,
        executed=True,
        message="Current time is 10:00 AM",
    )
    record = build_command_record(result, duration_ms=42)
    assert record["command"] == "what time is it"
    assert record["intent"] == "GET_TIME"
    assert record["subsystem"] == "CORE"
    assert record["execution_state"] == "COMPLETED"
    assert record["duration_ms"] == 42
    assert record["audit_status"] == "RECORDED"


def test_build_command_record_blocked():
    intent = IntentResult(intent="FORMAT_DISK", entities={}, confidence=1.0)
    result = PipelineResult(
        input="format disk",
        intent=intent,
        blocked=True,
        executed=False,
        message="Blocked by policy",
        reasoning={
            "analysis": {"risk": "CRITICAL"},
            "decision": {"decision": "BLOCK", "message": "Blocked by policy"},
        },
    )
    record = build_command_record(result, 10)
    assert record["execution_state"] == "BLOCKED"
    assert record["permission_state"] == "DENIED"
    assert record["risk_level"] == "CRITICAL"
    assert "FORTRESS" in record["why"]


def test_route_ask_agent():
    intent = IntentResult(
        intent="ASK_AGENT",
        entities={"agent": "nova", "query": "AI trends"},
        confidence=0.9,
    )
    result = PipelineResult(input="ask nova about AI", intent=intent, executed=True, message="Analysis...")
    record = build_command_record(result, 100)
    assert record["subsystem"] == "NOVA"
