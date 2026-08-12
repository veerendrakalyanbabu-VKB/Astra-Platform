from astra.core.intent.intents import RUN_GOAL
from astra.core.planner.plan import Plan
from astra.core.planner.routines import list_routines, resolve_routine


class GoalPlanner:
    """Creates single-step or multi-step plans from classified intents."""

    def __init__(self, routine_store=None):
        self.routine_store = routine_store

    def create_plan(self, intent_result):
        if intent_result.intent == RUN_GOAL:
            return self._create_goal_plan(intent_result)

        return Plan(
            action=intent_result.intent,
            parameters=intent_result.entities,
        )

    def _create_goal_plan(self, intent_result):
        goal_name = intent_result.entities.get("goal", "")
        routine_key, routine = resolve_routine(goal_name, self.routine_store)

        if not routine:
            return Plan(
                action=RUN_GOAL,
                parameters={
                    "goal": goal_name,
                    "available": list_routines(self.routine_store),
                },
            )

        return Plan(
            action=RUN_GOAL,
            parameters={
                "goal": routine_key,
                "title": routine["title"],
                "description": routine["description"],
            },
            steps=list(routine["steps"]),
        )
