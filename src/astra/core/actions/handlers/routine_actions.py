from typing import Dict

from astra.core.intent.intents import CREATE_ROUTINE, DELETE_ROUTINE, LIST_ROUTINES
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult
from astra.core.planner.routine_parser import parse_steps


class CreateRoutineHandler(ActionHandler):

    def __init__(self, routine_store):
        self.routine_store = routine_store

    def can_handle(self, action: str) -> bool:
        return action == CREATE_ROUTINE

    def execute(self, parameters: Dict) -> ActionResult:
        key = parameters.get("key", "").lower().replace(" ", "_")
        steps_text = parameters.get("steps", "")
        title = parameters.get("title", key.replace("_", " ").title())

        if not key or not steps_text:
            return ActionResult(
                success=False,
                message="Usage: create routine myday: get time, open notepad, show memory",
                error="INVALID_ROUTINE",
            )

        steps, errors = parse_steps(steps_text)

        if errors:
            return ActionResult(
                success=False,
                message=f"Unknown steps: {', '.join(errors)}. Try: get time, open chrome, show memory",
                error="UNKNOWN_STEPS",
            )

        if not steps:
            return ActionResult(
                success=False,
                message="No valid steps found.",
                error="EMPTY_ROUTINE",
            )

        self.routine_store.save_routine(key, title, steps)

        return ActionResult(
            success=True,
            message=f"Saved routine '{key}' with {len(steps)} steps. Run it with: run {key}",
            data={"key": key, "steps": len(steps)},
        )


class ListRoutinesHandler(ActionHandler):

    def __init__(self, routine_store):
        self.routine_store = routine_store

    def can_handle(self, action: str) -> bool:
        return action == LIST_ROUTINES

    def execute(self, parameters: Dict) -> ActionResult:
        from astra.core.planner.routines import list_routines

        routines = list_routines(self.routine_store)
        lines = ["Available routines:"]

        for routine in routines:
            tag = "custom" if routine.get("custom") else "built-in"
            lines.append(
                f"  {routine['key']} ({tag}, {routine['steps']} steps): {routine['title']}"
            )

        lines.append("")
        lines.append('Create your own: create routine myday: get time, open notepad')

        return ActionResult(
            success=True,
            message="\n".join(lines),
            data={"routines": routines},
        )


class DeleteRoutineHandler(ActionHandler):

    def __init__(self, routine_store):
        self.routine_store = routine_store

    def can_handle(self, action: str) -> bool:
        return action == DELETE_ROUTINE

    def execute(self, parameters: Dict) -> ActionResult:
        key = parameters.get("key", "").lower().replace(" ", "_")

        if not key:
            return ActionResult(
                success=False,
                message="Usage: delete routine myday",
                error="MISSING_KEY",
            )

        if not self.routine_store.delete_routine(key):
            return ActionResult(
                success=False,
                message=f"Custom routine '{key}' not found.",
                error="NOT_FOUND",
            )

        return ActionResult(
            success=True,
            message=f"Deleted custom routine '{key}'.",
            data={"key": key},
        )
