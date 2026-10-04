# goal_conditions.py

from abc import ABC, abstractmethod


class GoalCondition:

    def evaluate(self, candidate, state):
        raise NotImplementedError

class FitsMeasurements(GoalCondition):

    def __init__(self, measurements, tolerance=0.01):
        self.measurements = measurements
        self.tolerance = tolerance

    def evaluate(self, candidate, state):
        print(candidate)
        model = candidate["expression"]

        residuals = []

        for measurement in self.measurements:

            t = measurement["t"]
            x_true = measurement["x"]
            y_true = measurement["y"]

            x_pred = model["x"](t)
            y_pred = model["y"](t)

            residuals.append(
                (x_pred - x_true)**2 +
                (y_pred - y_true)**2
            )

        mse = sum(residuals) / len(residuals)

        return mse < self.tolerance, mse


class DerivativeEqualsZero(GoalCondition):

    def __init__(self, target):
        self.target = target

    def evaluate(self, candidate, state):

        node = candidate["node"]

        # Must be a solution
        if node["type"] != "solution":
            return False

        # It must come from a derivative equation
        parents = node.get("parents", [])

        for parent_id in parents:

            parent = state["equations"][parent_id]

            if parent["type"] == "derivative":
                return True, 0

        return False, 1


class SecondDerivativePositive(GoalCondition):

    def __init__(self, target):
        self.target = target

    def evaluate(self, candidate, state):

        solution = candidate["node"]["expression"]

        x = solution.rhs

        function = state["equations"]["eq1"]

        second = diff(
            function["expression"],
            function["variable"],
            2
        )

        value = second.subs(
            function["variable"],
            x
        )

        return value > 0, 0
