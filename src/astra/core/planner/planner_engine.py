from astra.core.planner.planner_rules import PlannerRules


class PlannerEngine:

    def __init__(self):
        self.rules = PlannerRules()

    def plan(self, intent_result):

        return self.rules.create_plan(intent_result)