class Validator:
    """
    Validates whether Astra should execute
    the requested action.
    """

    def validate(self, analysis):

        risk = analysis["risk"]

        if risk == "CRITICAL":
            return False

        return True