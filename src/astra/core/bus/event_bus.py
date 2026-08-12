from collections import defaultdict
from typing import Callable, Dict, List


class EventBus:
    """
    In-process publish/subscribe message bus.
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable) -> None:
        self._subscribers[event_type].append(handler)

    def publish(self, event_type: str, payload: dict) -> None:
        for handler in self._subscribers[event_type]:
            handler(payload)

        for handler in self._subscribers["*"]:
            handler({"event": event_type, **payload})

    def clear(self) -> None:
        self._subscribers.clear()
