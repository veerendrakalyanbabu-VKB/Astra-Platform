from typing import Dict

from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


class TimerHandler(ActionHandler):

    def can_handle(self, action: str) -> bool:
        return action == "SET_TIMER"

    def execute(self, parameters: Dict) -> ActionResult:
        minutes = parameters.get("minutes", 5)
        return ActionResult(
            success=True,
            message=f"Timer set for {minutes} minutes. (Demo plugin — use a real timer app for now.)",
            data={"plugin": "timer", "minutes": minutes},
        )


def register(core):
    core.register_plugin_intent(
        "SET_TIMER",
        ("set timer", "timer 5 minutes", "start timer"),
        TimerHandler(),
    )
