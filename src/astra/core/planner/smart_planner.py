"""Context-aware smart goal planning."""

from astra.core.intent.intents import RUN_GOAL, ACTIVATE_WORKSPACE
from astra.core.planner.goal_planner import GoalPlanner
from astra.core.planner.llm_decomposer import LLMGoalDecomposer
from astra.core.planner.plan import Plan
from astra.core.planner.routine_parser import parse_steps
from astra.core.planner.routines import list_routines, resolve_routine
from astra.core.planner.workspace import resolve_workspace


KEYWORD_PLANS = {
    "work morning": ["get time", "system info", "open code"],
    "work": ["system info", "open code", "get time"],
    "relax": ["set volume 30", "open chrome", "get time"],
    "study": ["get time", "open notepad", "minimize all"],
    "cleanup": ["list windows", "minimize all", "show memory"],
}


class SmartPlanner(GoalPlanner):
    """Goal planner with rule-based and optional LLM decomposition."""

    def __init__(self, routine_store=None, memory_manager=None, llm_enabled: bool = None):
        super().__init__(routine_store)
        self.memory = memory_manager
        self.decomposer = LLMGoalDecomposer(enabled=llm_enabled)

    def create_plan(self, intent_result):
        if intent_result.intent == ACTIVATE_WORKSPACE:
            return self._create_workspace_plan(intent_result)

        if intent_result.intent == RUN_GOAL:
            return self._create_goal_plan(intent_result)

        return Plan(
            action=intent_result.intent,
            parameters=intent_result.entities,
        )

    def _create_workspace_plan(self, intent_result):
        workspace_name = intent_result.entities.get("workspace", "")
        key, workspace = resolve_workspace(workspace_name)

        if not workspace:
            return Plan(
                action=RUN_GOAL,
                parameters={"goal": workspace_name, "available": list_routines(self.routine_store)},
            )

        return Plan(
            action=RUN_GOAL,
            parameters={
                "goal": key,
                "title": workspace["title"],
                "description": workspace["description"],
                "source": "workspace",
            },
            steps=list(workspace["steps"]),
        )

    def _create_goal_plan(self, intent_result):
        goal_name = intent_result.entities.get("goal", "")

        steps = self._decompose_goal(goal_name)
        if steps:
            return Plan(
                action=RUN_GOAL,
                parameters={
                    "goal": goal_name,
                    "title": goal_name.title(),
                    "description": "Smart plan",
                    "source": "smart",
                },
                steps=steps,
            )

        routine_key, routine = resolve_routine(goal_name, self.routine_store)

        if routine:
            return Plan(
                action=RUN_GOAL,
                parameters={
                    "goal": routine_key,
                    "title": routine["title"],
                    "description": routine["description"],
                    "source": "routine",
                },
                steps=list(routine["steps"]),
            )

        return Plan(
            action=RUN_GOAL,
            parameters={
                "goal": goal_name,
                "available": list_routines(self.routine_store),
            },
        )

    def _decompose_goal(self, goal_name: str):
        normalized = goal_name.lower().strip()

        if "," in normalized:
            steps, errors = parse_steps(normalized)
            if steps and not errors:
                return steps

        for key, step_strings in KEYWORD_PLANS.items():
            if key in normalized:
                combined = ", ".join(step_strings)
                steps, errors = parse_steps(combined)
                if steps and not errors:
                    return steps

        memory_hints = self.memory.list_all() if self.memory else {}
        llm_steps = self.decomposer.decompose(goal_name, memory_hints)

        if llm_steps:
            return llm_steps

        return None
