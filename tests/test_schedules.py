import pytest

from astra.core.planner.scheduler import RoutineScheduler


def test_schedule_morning_brief_command(tmp_path):
    sched = RoutineScheduler(tmp_path)
    entry = sched.add("morning_brief", "8am")
    assert entry["command"] == "morning brief"
    assert entry["time"] == "08:00"


def test_schedule_startup_protocol(tmp_path):
    sched = RoutineScheduler(tmp_path)
    entry = sched.add("startup_protocol", "7:30am")
    assert entry["command"] == "run startup protocol"


def test_run_due_executes_once_per_day(tmp_path):
    sched = RoutineScheduler(tmp_path)
    sched.add("morning_brief", "08:00")

    from datetime import datetime
    from unittest.mock import patch

    calls = []

    def runner(cmd, entry):
        calls.append(cmd)
        return {"message": "brief ok"}

    with patch("astra.core.planner.scheduler.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2026, 8, 12, 8, 0)
        mock_dt.strftime = datetime.strftime
        executed = sched.run_due(runner)

    assert len(executed) == 1
    assert executed[0]["command"] == "morning brief"
    assert len(calls) == 1

    with patch("astra.core.planner.scheduler.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2026, 8, 12, 8, 0)
        mock_dt.strftime = datetime.strftime
        again = sched.run_due(runner)

    assert len(again) == 0


def test_list_schedules_intent():
    from astra.core.intent.intent_engine import IntentEngine
    from astra.core.intent.intents import LIST_SCHEDULES

    engine = IntentEngine(llm_enabled=False)
    assert engine.process("list schedules").intent == LIST_SCHEDULES


def test_schedule_multiword_intent():
    from astra.core.intent.intent_engine import IntentEngine
    from astra.core.intent.intents import SCHEDULE_ROUTINE

    engine = IntentEngine(llm_enabled=False)
    result = engine.process("schedule morning brief at 8am")
    assert result.intent == SCHEDULE_ROUTINE
    assert result.entities["routine"] == "morning_brief"
