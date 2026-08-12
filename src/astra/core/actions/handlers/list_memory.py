from typing import Dict

from astra.core.intent.intents import LIST_MEMORY
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


class ListMemoryHandler(ActionHandler):

    def __init__(self, memory_manager):
        self.memory = memory_manager

    def can_handle(self, action: str) -> bool:
        return action == LIST_MEMORY

    def execute(self, parameters: Dict) -> ActionResult:
        entries = self.memory.list_all()

        if not entries:
            return ActionResult(
                success=True,
                message="I don't have anything stored in memory yet.",
                data={"entries": {}},
            )

        lines = [f"  {key}: {value}" for key, value in entries.items()]
        formatted = "Here is what I remember:\n" + "\n".join(lines)

        return ActionResult(
            success=True,
            message=formatted,
            data={"entries": entries},
        )
