from typing import Dict

from astra.core.intent.intents import RECALL_MEMORY
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


class RecallMemoryHandler(ActionHandler):

    def __init__(self, memory_manager):
        self.memory = memory_manager

    def can_handle(self, action: str) -> bool:
        return action == RECALL_MEMORY

    def execute(self, parameters: Dict) -> ActionResult:
        query = parameters.get("query", "").strip()

        if not query:
            return ActionResult(
                success=False,
                message="What would you like me to recall?",
                error="EMPTY_QUERY",
            )

        value = self.memory.recall_best(query)

        if value is None:
            return ActionResult(
                success=False,
                message=f"I don't have anything stored about '{query}'.",
                error="NOT_FOUND",
            )

        return ActionResult(
            success=True,
            message=f"I remember: {value}",
            data={"query": query, "value": value},
        )
