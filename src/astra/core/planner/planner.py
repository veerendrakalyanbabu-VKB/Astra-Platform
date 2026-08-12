from .plan import Plan


class Planner:

    def create_plan(self, intent_result):

        return Plan(
            action=intent_result.intent,
            parameters=intent_result.entities
        )