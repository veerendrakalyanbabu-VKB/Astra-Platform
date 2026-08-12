import re
from datetime import datetime
from typing import Dict

from astra.core.intent.intents import SAVE_MEMORY
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


class SaveMemoryHandler(ActionHandler):

    def __init__(self, memory_manager):
        self.memory = memory_manager

    def can_handle(self, action: str) -> bool:
        return action == SAVE_MEMORY

    def execute(self, parameters: Dict) -> ActionResult:
        text = parameters.get("text", "").strip()

        if not text:
            return ActionResult(
                success=False,
                message="Nothing to remember.",
                error="EMPTY_MEMORY_TEXT",
            )

        key = self._derive_key(text)
        self.memory.remember(key, text)

        return ActionResult(
            success=True,
            message=f"Saved to memory as '{key}'.",
            data={"key": key, "text": text},
        )

    def _derive_key(self, text: str) -> str:
        match = re.match(r"my\s+(.+?)\s+is\s+(.+)", text, re.IGNORECASE)

        if match:
            subject = match.group(1).strip().lower()
            subject = re.sub(r"[^\w\s]", "", subject)
            subject = re.sub(r"\s+", "_", subject)
            return subject

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"memory_{timestamp}"
