from typing import Dict

from astra.core.intent.intents import RUN_GOAL
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult
from astra.core.planner.routines import list_routines


class RunGoalHandler(ActionHandler):

    def can_handle(self, action: str) -> bool:
        return action == RUN_GOAL

    def execute(self, parameters: Dict) -> ActionResult:
        if parameters.get("available"):
            lines = ["Available routines:"]

            for routine in parameters["available"]:
                lines.append(
                    f"  {routine['key']}: {routine['title']} "
                    f"({routine['steps']} steps) — {routine['description']}"
                )

            lines.append("")
            lines.append('Try: "organize my morning routine"')

            return ActionResult(
                success=True,
                message="\n".join(lines),
            )

        title = parameters.get("title", parameters.get("goal", "goal"))
        description = parameters.get("description", "")

        return ActionResult(
            success=True,
            message=f"Starting routine: {title}. {description}".strip(),
            data={"goal": parameters.get("goal"), "title": title},
        )
