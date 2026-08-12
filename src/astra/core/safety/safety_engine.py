import json
from pathlib import Path


DEFAULT_POLICIES = {
    "rules": [
        {"action": "FORMAT_DISK", "decision": "BLOCK"},
        {"action": "DELETE_FILE", "decision": "CONFIRM", "max_per_session": 5},
        {"action": "SHUTDOWN_PC", "decision": "CONFIRM"},
    ]
}


class SafetyEngine:
    """
    Policy-based safety enforcement beyond basic risk analysis.
    """

    def __init__(self, policy_path: Path = None):
        self.policy_path = policy_path or Path("data/policies.json")
        self.policies = self._load_policies()
        self._session_counts = {}

    def _load_policies(self) -> dict:
        if not self.policy_path.exists():
            self.policy_path.parent.mkdir(parents=True, exist_ok=True)
            self.policy_path.write_text(
                json.dumps(DEFAULT_POLICIES, indent=4),
                encoding="utf-8",
            )
            return DEFAULT_POLICIES

        with open(self.policy_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def evaluate(self, plan, base_decision: str) -> dict:
        action = plan.action
        rule = self._find_rule(action)

        if not rule:
            return {
                "decision": base_decision,
                "message": None,
                "policy": None,
            }

        policy_decision = rule.get("decision", base_decision)

        if policy_decision == "BLOCK":
            return {
                "decision": "BLOCK",
                "message": f"Policy blocked action '{action}'.",
                "policy": rule,
            }

        max_per_session = rule.get("max_per_session")

        if max_per_session is not None:
            count = self._session_counts.get(action, 0)

            if count >= max_per_session:
                return {
                    "decision": "BLOCK",
                    "message": (
                        f"Policy limit reached: '{action}' allowed "
                        f"{max_per_session} times per session."
                    ),
                    "policy": rule,
                }

        if policy_decision == "CONFIRM" and base_decision == "EXECUTE":
            return {
                "decision": "CONFIRM",
                "message": f"Policy requires confirmation for '{action}'.",
                "policy": rule,
            }

        if policy_decision == "CONFIRM":
            return {
                "decision": "CONFIRM",
                "message": f"Policy requires confirmation for '{action}'.",
                "policy": rule,
            }

        return {
            "decision": base_decision,
            "message": None,
            "policy": rule,
        }

    def record_execution(self, action: str) -> None:
        self._session_counts[action] = self._session_counts.get(action, 0) + 1

    def _find_rule(self, action: str):
        for rule in self.policies.get("rules", []):
            if rule.get("action") == action:
                return rule
        return None

    def reset_session(self) -> None:
        self._session_counts.clear()
