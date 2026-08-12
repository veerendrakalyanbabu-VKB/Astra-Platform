from astra.core.intent.intents import RUN_GOAL
from astra.core.intent.models import IntentResult
from astra.core.planner.goal_planner import GoalPlanner


def test_goal_planner_morning_routine():
    planner = GoalPlanner()
    intent = IntentResult(intent=RUN_GOAL, entities={"goal": "morning routine"}, confidence=1.0)

    plan = planner.create_plan(intent)

    assert plan.is_multi_step
    assert len(plan.steps) == 3
    assert plan.parameters["title"] == "Morning Routine"


def test_goal_planner_unknown_routine():
    planner = GoalPlanner()
    intent = IntentResult(intent=RUN_GOAL, entities={"goal": "unknown xyz"}, confidence=1.0)

    plan = planner.create_plan(intent)

    assert not plan.is_multi_step
    assert plan.parameters.get("available")


def test_goal_planner_focus_mode():
    planner = GoalPlanner()
    intent = IntentResult(intent=RUN_GOAL, entities={"goal": "focus mode"}, confidence=1.0)

    plan = planner.create_plan(intent)

    assert plan.is_multi_step
    assert plan.parameters["goal"] == "focus"
