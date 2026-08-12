from typing import Dict

from astra.core.intent.intents import CALCULATE
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


class CalculateHandler(ActionHandler):

    def __init__(self, tool_manager):
        self.tools = tool_manager

    def can_handle(self, action: str) -> bool:
        return action == CALCULATE

    def execute(self, parameters: Dict) -> ActionResult:
        expression = parameters.get("expression", "").strip()

        if not expression:
            return ActionResult(
                success=False,
                message="What should I calculate?",
                error="EMPTY_EXPRESSION",
            )

        result = self.tools.invoke("calculator", {"expression": expression})

        if not result["success"]:
            return ActionResult(
                success=False,
                message=f"Calculation failed: {result.get('error', 'unknown error')}",
                error="CALCULATION_FAILED",
            )

        value = result["result"]["result"]

        return ActionResult(
            success=True,
            message=f"{expression} = {value}",
            data=result["result"],
        )
