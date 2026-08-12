from astra.core.planner.smart_planner import SmartPlanner
from astra.core.intent.models import IntentResult
from astra.core.intent.intents import RUN_GOAL, ACTIVATE_WORKSPACE


def test_smart_planner_keyword_plan():
    planner = SmartPlanner()
    intent = IntentResult(intent=RUN_GOAL, entities={"goal": "study session"}, confidence=1.0)

    plan = planner.create_plan(intent)

    assert plan.is_multi_step
    assert plan.parameters.get("source") == "smart"


def test_smart_planner_workspace():
    planner = SmartPlanner()
    intent = IntentResult(
        intent=ACTIVATE_WORKSPACE,
        entities={"workspace": "coding"},
        confidence=1.0,
    )

    plan = planner.create_plan(intent)

    assert plan.is_multi_step
    assert plan.parameters.get("source") == "workspace"


def test_smart_planner_builtin_routine():
    planner = SmartPlanner()
    intent = IntentResult(intent=RUN_GOAL, entities={"goal": "morning"}, confidence=1.0)

    plan = planner.create_plan(intent)

    assert plan.is_multi_step
    assert plan.parameters.get("source") == "routine"
