# goal_conditions.py

from abc import ABC, abstractmethod


class GoalCondition:

    def evaluate(self, candidate, state):
        raise NotImplementedError


class FitsMeasurements(GoalCondition):
    """
    Candidate predicts outputs y=f(x).

    x and y may be vectors of arbitrary dimension.

    Notice that (x_i, y_i) can naturally be

    x_i ∈ R^m
    y_i ∈ R^n

    so this covers

    scalar regression
    multivariate regression
    trajectories
    PDE snapshots
    robot trajectories
    astronomical observations

    without changing anything.
    """

    def __init__(self, measurements, tolerance=None):
        self.measurements = measurements
        self.tolerance = tolerance

    def evaluate(self, candidate, state):

        residuals = []

        for x_i, y_i in self.measurements:

            y_pred = candidate(x_i)

            residuals.append(y_pred - y_i)

        variance_residual = variance(residuals)

        score = variance_residual

        if self.tolerance is None:
            success = False

        else:
            success = variance_residual <= self.tolerance

        return success, score


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
