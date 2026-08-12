from typing import Dict

from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


QUOTES = [
    "The brain is built. Now we build the world around it.",
    "Intent first. Everything else follows.",
    "Small routines compound into big mornings.",
]


class QuotesHandler(ActionHandler):

    def can_handle(self, action: str) -> bool:
        return action == "GET_QUOTE"

    def execute(self, parameters: Dict) -> ActionResult:
        import random
        quote = random.choice(QUOTES)
        return ActionResult(
            success=True,
            message=f"Quote: {quote}",
            data={"plugin": "quotes", "quote": quote},
        )


def register(core):
    core.register_plugin_intent(
        "GET_QUOTE",
        ("give me a quote", "inspire me", "daily quote", "motivate me"),
        QuotesHandler(),
    )
