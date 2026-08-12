class PermissionManager:
    """
    Manages user consent for privileged actions.
    Holds pending plans awaiting confirmation.
    """

    YES_RESPONSES = frozenset({
        "yes", "y", "yeah", "yep", "confirm", "proceed",
        "do it", "go ahead", "ok", "okay", "sure",
    })

    NO_RESPONSES = frozenset({
        "no", "n", "nope", "cancel", "abort", "stop",
        "dont", "don't", "never mind", "nevermind",
    })

    def __init__(self):
        self._pending_plan = None
        self._pending_reasoning = None

    def request_confirmation(self, plan, reasoning):
        self._pending_plan = plan
        self._pending_reasoning = reasoning

    def has_pending(self) -> bool:
        return self._pending_plan is not None

    @property
    def pending_plan(self):
        return self._pending_plan

    @property
    def pending_reasoning(self):
        return self._pending_reasoning

    def approve(self):
        plan = self._pending_plan
        self.clear()
        return plan

    def deny(self):
        self.clear()

    def clear(self):
        self._pending_plan = None
        self._pending_reasoning = None

    def parse_confirmation(self, text: str):
        normalized = text.lower().strip()

        if normalized in self.YES_RESPONSES:
            return True

        if normalized in self.NO_RESPONSES:
            return False

        return None

    def describe_pending(self) -> str:
        if not self._pending_plan:
            return ""

        action = self._pending_plan.action
        risk = "UNKNOWN"

        if self._pending_reasoning:
            risk = self._pending_reasoning["analysis"]["risk"]

        params = self._pending_plan.parameters
        detail = ", ".join(f"{k}={v}" for k, v in params.items()) if params else "none"

        return (
            f"Action '{action}' is classified as {risk} risk "
            f"(parameters: {detail})."
        )
