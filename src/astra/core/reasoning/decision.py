class DecisionMaker:
    """
    Makes the final execution decision.
    """

    RISK_MESSAGES = {
        "HIGH": "This action is high risk and requires your confirmation.",
        "CRITICAL": "This action is critically dangerous and cannot be executed.",
    }

    def decide(self, analysis, valid):

        if not valid:
            return {
                "decision": "BLOCK",
                "message": self.RISK_MESSAGES.get(
                    analysis["risk"],
                    "Execution blocked for safety.",
                ),
            }

        risk = analysis["risk"]

        if risk == "HIGH":
            return {
                "decision": "CONFIRM",
                "message": self.RISK_MESSAGES["HIGH"],
            }

        return {
            "decision": "EXECUTE",
            "message": "Safe to execute.",
        }
