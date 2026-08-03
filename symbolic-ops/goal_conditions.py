# goal_conditions.py

from abc import ABC, abstractmethod


class GoalCondition(ABC):
    """
    A mathematical condition that a candidate solution must satisfy.
    """

    @abstractmethod
    def evaluate(self, candidate, state):
        """
        Returns
        -------
        success : bool
        score : float

        score is 0 for a perfect solution and increases with error.
        """
        pass


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

    def __init__(self, function):
        self.function = function

    def evaluate(self, candidate, state):

        variable = self.function["variable"]
        expression = self.function["expression"]

        derivative = sp.diff(expression, variable)

        value = derivative.subs(variable, candidate)

        success = sp.simplify(value) == 0

        score = abs(float(value))

        return success, score
