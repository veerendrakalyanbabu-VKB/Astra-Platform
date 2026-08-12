from astra.core.planner.plan import Plan


class Analyzer:
    """
    Examines the execution plan and determines
    whether there are any obvious risks.
    """

    HIGH_RISK_ACTIONS = {"DELETE_FILE", "SHUTDOWN_PC"}
    CRITICAL_ACTIONS = {"FORMAT_DISK"}

    def analyze(self, plan):

        if plan.is_multi_step:
            highest = "LOW"

            for step in plan.steps:
                step_analysis = self.analyze(Plan(step.action, step.parameters))
                risk = step_analysis["risk"]

                if risk == "CRITICAL":
                    return {
                        "goal": plan.action,
                        "risk": "CRITICAL",
                    }

                if risk == "HIGH":
                    highest = "HIGH"

            return {
                "goal": plan.action,
                "risk": highest,
            }

        action = plan.action

        if action in self.CRITICAL_ACTIONS:
            return {
                "goal": action,
                "risk": "CRITICAL",
            }

        if action in self.HIGH_RISK_ACTIONS:
            return {
                "goal": action,
                "risk": "HIGH",
            }

        return {
            "goal": action,
            "risk": "LOW",
        }
