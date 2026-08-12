from astra.core.reasoning.analyzer import Analyzer
from astra.core.reasoning.validator import Validator
from astra.core.reasoning.decision import DecisionMaker


class ReasoningEngine:

    def __init__(self):

        self.analyzer = Analyzer()
        self.validator = Validator()
        self.decision = DecisionMaker()

    def think(self, plan):

        analysis = self.analyzer.analyze(plan)

        valid = self.validator.validate(analysis)

        decision = self.decision.decide(
            analysis,
            valid
        )

        return {
            "analysis": analysis,
            "decision": decision
        }