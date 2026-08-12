from typing import Dict

from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


class WeatherHandler(ActionHandler):

    def can_handle(self, action: str) -> bool:
        return action == "GET_WEATHER"

    def execute(self, parameters: Dict) -> ActionResult:
        return ActionResult(
            success=True,
            message="Weather report: Clear skies, 72°F, light breeze. (Demo plugin)",
            data={"plugin": "weather", "condition": "clear", "temp_f": 72},
        )


def register(core):
    core.register_plugin_intent(
        "GET_WEATHER",
        ("weather report", "what's the weather", "whats the weather", "get weather"),
        WeatherHandler(),
    )
