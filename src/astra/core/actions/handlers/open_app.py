from typing import Dict

from astra.core.intent.intents import OPEN_APP
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


class OpenAppHandler(ActionHandler):

    def __init__(self, windows_layer=None):
        if windows_layer is None:
            from astra.core.os import WindowsLayer
            windows_layer = WindowsLayer()
        self.windows = windows_layer

    def can_handle(self, action: str) -> bool:
        return action == OPEN_APP

    def execute(self, parameters: Dict) -> ActionResult:
        application = parameters.get("application", "")
        result = self.windows.launch_app(application)

        return ActionResult(
            success=result["success"],
            message=result["message"],
            data=result.get("data"),
            error=result.get("error"),
        )
