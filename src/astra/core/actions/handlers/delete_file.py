from typing import Dict

from astra.core.intent.intents import DELETE_FILE
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


class DeleteFileHandler(ActionHandler):
    """
    Simulated delete handler.
    Does not perform real file deletion — validates the safety pipeline.
    """

    def can_handle(self, action: str) -> bool:
        return action == DELETE_FILE

    def execute(self, parameters: Dict) -> ActionResult:
        target = parameters.get("target", "").strip()

        if not target:
            return ActionResult(
                success=False,
                message="No file specified for deletion.",
                error="MISSING_TARGET",
            )

        return ActionResult(
            success=True,
            message=f"Simulated deletion of '{target}' completed.",
            data={"target": target, "simulated": True},
        )
