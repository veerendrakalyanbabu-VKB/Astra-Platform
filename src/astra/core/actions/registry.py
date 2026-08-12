from typing import Dict, List, Optional

from astra.core.actions.handlers.base import ActionHandler


class ActionRegistry:

    def __init__(self):
        self._handlers: List[ActionHandler] = []

    def register(self, handler: ActionHandler) -> None:
        self._handlers.append(handler)

    def get_handler(self, action: str) -> Optional[ActionHandler]:
        for handler in self._handlers:
            if handler.can_handle(action):
                return handler
        return None

    def list_actions(self) -> List[str]:
        return [handler.__class__.__name__ for handler in self._handlers]
