from astra.core.planner.plan import Plan


class PlannerRules:

    def create_plan(self, intent_result):

        intent = intent_result.intent
        entities = intent_result.entities

        if intent == "OPEN_APP":
            return Plan(
                action="OPEN_APP",
                parameters=entities
            )

        elif intent == "SAVE_MEMORY":
            return Plan(
                action="SAVE_MEMORY",
                parameters=entities
            )

        elif intent == "GET_TIME":
            return Plan(
                action="GET_TIME",
                parameters={}
            )

        return Plan(
            action="UNKNOWN",
            parameters={}
        )
