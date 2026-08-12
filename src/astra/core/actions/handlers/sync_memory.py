from typing import Dict

from astra.core.intent.intents import SYNC_MEMORY
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


class SyncMemoryHandler(ActionHandler):

    def __init__(self, cloud_sync):
        self.cloud_sync = cloud_sync

    def can_handle(self, action: str) -> bool:
        return action == SYNC_MEMORY

    def execute(self, parameters: Dict) -> ActionResult:
        result = self.cloud_sync.sync()

        message = (
            f"{result['message']} "
            f"Exported {result['exported_keys']} keys. "
            f"Device: {result['device_id'][:8]}..."
        )

        if result.get("imported"):
            message += f" Imported {result['imported']} keys."

        return ActionResult(
            success=True,
            message=message,
            data=result,
        )
