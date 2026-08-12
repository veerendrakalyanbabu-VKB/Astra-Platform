import pytest
from pathlib import Path

from astra.core.billing.tiers import TierManager, tier_includes_agent, TIERS
from astra.core.agents import squad
from astra.core.modes.workspace_mode import WorkspaceMode, MODES


@pytest.fixture
def tier_manager(tmp_path):
    return TierManager(tmp_path)


def test_cosmic_tier_default(tier_manager):
    assert tier_manager.tier_id == "cosmic"
    assert tier_manager.has_feature("student_mode") is True
    assert tier_manager.has_feature("morning_brief") is False


def test_demo_activate_startup(tier_manager):
    result = tier_manager.demo_activate("startup")
    assert result["success"] is True
    assert tier_manager.tier_id == "startup"
    assert tier_manager.has_feature("morning_brief") is True


def test_squad_agents_locked_on_free():
    agents = squad.list_agents("cosmic")
    mentor = next(a for a in agents if a["id"] == "mentor")
    assert mentor["locked"] is True
    assert mentor["online"] is True
    assert tier_includes_agent("startup", "mentor") is True


def test_workspace_mode_student(tmp_path):
    from astra.core.memory.memory_manager import MemoryManager

    memory = MemoryManager()
    memory.data_folder = tmp_path / "data"
    memory.memory_file = memory.data_folder / "memory.json"
    memory.data_folder.mkdir(parents=True)
    memory.memory_file.write_text("{}", encoding="utf-8")

    tiers = TierManager(tmp_path)
    modes = WorkspaceMode(memory, tiers)
    result = modes.set_mode("student")
    assert result["success"] is True
    assert modes.get_mode() == "student"


def test_morning_brief_cosmic_lite(tmp_path):
    from astra.core.astra_core import AstraCore

    core = AstraCore(project_root=tmp_path)
    core.initialize()
    brief = core.morning_brief.generate()
    assert brief["available"] is True
    assert len(brief["lines"]) > 0
    assert brief["tier"] == "cosmic"

    core.tiers.demo_activate("startup")
    brief = core.morning_brief.generate()
    assert brief["available"] is True
    assert brief["tier"] == "full"
    assert len(brief["lines"]) > 0


def test_intent_show_squad():
    from astra.core.intent.intent_engine import IntentEngine
    from astra.core.intent.intents import SHOW_SQUAD, SHOW_PLANS, MORNING_BRIEF, SET_MODE

    engine = IntentEngine(llm_enabled=False)
    assert engine.process("show squad").intent == SHOW_SQUAD
    assert engine.process("show plans").intent == SHOW_PLANS
    assert engine.process("morning brief").intent == MORNING_BRIEF
    assert engine.process("student mode").intent == SET_MODE


def test_activate_plan_intent():
    from astra.core.intent.intent_engine import IntentEngine
    from astra.core.intent.intents import ACTIVATE_PLAN

    engine = IntentEngine(llm_enabled=False)
    result = engine.process("activate startup plan")
    assert result.intent == ACTIVATE_PLAN
    assert result.entities["tier"] == "startup"
