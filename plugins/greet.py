from typing import Dict

from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


class GreetHandler(ActionHandler):

    def can_handle(self, action: str) -> bool:
        return action == "SAY_HELLO"

    def execute(self, parameters: Dict) -> ActionResult:
        return ActionResult(
            success=True,
            message="Hello from the Astra plugin system! Plugins are working.",
            data={"plugin": "greet"},
        )


def register(core):
    core.register_plugin_intent(
        "SAY_HELLO",
        ("hello astra", "greet me", "say hello"),
        GreetHandler(),
    )
