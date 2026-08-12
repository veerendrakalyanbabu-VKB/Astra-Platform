from astra.core.intent.intents import OPEN_APP, GET_TIME


class ContextResolver:
    """
    Resolves ambiguous or follow-up commands using session context.
    Runs before standard classification.
    """

    REOPEN_PHRASES = (
        "open it again",
        "launch it again",
        "start it again",
        "run it again",
        "same app",
        "same application",
        "again",
        "one more time",
    )

    REPEAT_TIME_PHRASES = (
        "what about the time",
        "time again",
        "and the time",
    )

    def resolve(self, text: str, context) -> dict | None:
        normalized = text.strip().lower()

        if normalized in self.REOPEN_PHRASES:
            last_app = context.get_state("last_application")

            if last_app:
                return {
                    "intent": OPEN_APP,
                    "entities": {"application": last_app},
                    "confidence": 0.95,
                    "source": "context",
                }

        if normalized in self.REPEAT_TIME_PHRASES:
            return {
                "intent": GET_TIME,
                "entities": {},
                "confidence": 0.95,
                "source": "context",
            }

        return None
