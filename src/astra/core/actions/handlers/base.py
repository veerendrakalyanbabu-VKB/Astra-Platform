from abc import ABC, abstractmethod
from typing import Dict

from astra.core.actions.result import ActionResult


class ActionHandler(ABC):

    @abstractmethod
    def can_handle(self, action: str) -> bool:
        pass

    @abstractmethod
    def execute(self, parameters: Dict) -> ActionResult:
        pass
