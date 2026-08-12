import pytest

from astra.core.revolution.revolution_engine import RevolutionEngine, MANIFESTO
from astra.core.revolution.protocols import IndustrialProtocol, PROTOCOLS


@pytest.fixture
def revolution(tmp_path):
    return RevolutionEngine(tmp_path)


def test_revolution_stage_awakening(revolution):
    stage = revolution.stage()
    assert stage["id"] == "awakening"
    assert stage["total_commands"] == 0


def test_revolution_stage_progression(revolution):
    for _ in range(15):
        revolution.record_command(True, "OPEN_APP")
    assert revolution.stage()["id"] == "automation"


def test_automation_index(revolution):
    revolution.record_command(True, "ASK_AGENT")
    index = revolution.automation_index({"success_rate": 0.8})
    assert 0 <= index <= 99


def test_manifesto_present(revolution):
    assert "Industrial Revolution" in MANIFESTO


def test_protocol_list():
    assert "student" in PROTOCOLS
    assert "startup" in PROTOCOLS
    assert "revolution" in PROTOCOLS


def test_run_student_protocol(tmp_path):
    from astra.core.astra_core import AstraCore

    core = AstraCore(project_root=tmp_path)
    core.initialize()
    result = IndustrialProtocol(core).run("student")
    assert result["success"] is True
    assert "STUDENT" in result["message"].upper() or "Student" in result["message"]


def test_revolution_intents():
    from astra.core.intent.intent_engine import IntentEngine
    from astra.core.intent.intents import REVOLUTION_STATUS, RUN_PROTOCOL

    engine = IntentEngine(llm_enabled=False)
    assert engine.process("revolution status").intent == REVOLUTION_STATUS
    assert engine.process("industrial revolution").intent == RUN_PROTOCOL
    assert engine.process("run startup protocol").entities["protocol"] == "startup"
