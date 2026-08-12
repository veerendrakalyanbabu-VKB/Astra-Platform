class PlanStep:

    def __init__(self, action, parameters=None):
        self.action = action
        self.parameters = parameters or {}


class Plan:

    def __init__(self, action, parameters=None, steps=None):
        self.action = action
        self.parameters = parameters or {}
        self.steps = steps or []

    @property
    def is_multi_step(self) -> bool:
        return len(self.steps) > 0
