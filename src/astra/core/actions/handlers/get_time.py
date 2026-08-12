from datetime import datetime
from typing import Dict

from astra.core.intent.intents import GET_TIME
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


class GetTimeHandler(ActionHandler):

    def can_handle(self, action: str) -> bool:
        return action == GET_TIME

    def execute(self, parameters: Dict) -> ActionResult:
        now = datetime.now()
        formatted = now.strftime("%I:%M %p on %A, %B %d, %Y")

        return ActionResult(
            success=True,
            message=f"The current time is {formatted}.",
            data={
                "time": now.strftime("%H:%M:%S"),
                "date": now.strftime("%Y-%m-%d"),
                "formatted": formatted,
            },
        )
