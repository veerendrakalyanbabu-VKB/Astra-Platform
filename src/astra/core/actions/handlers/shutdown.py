from typing import Dict

from astra.core.intent.intents import SHUTDOWN_PC
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


class ShutdownHandler(ActionHandler):
    """
    Simulated shutdown handler.
    Does not shut down the system — validates the safety pipeline.
    """

    def can_handle(self, action: str) -> bool:
        return action == SHUTDOWN_PC

    def execute(self, parameters: Dict) -> ActionResult:
        return ActionResult(
            success=True,
            message="Simulated system shutdown initiated.",
            data={"simulated": True},
        )
