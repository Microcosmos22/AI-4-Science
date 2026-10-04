from sympy import *
from llama_cpp import Llama, LlamaGrammar
import json
from fitters.least_squares import fit

def differentiate(state, equation, variable):

    expr = state["equations"][equation]["expression"]

    result = diff(expr, Symbol(variable))

    return {
        "expression": result,
        "type": "derivative",
        "variable": variable,
        "parents": [equation],
        "generated_by": "differentiate",
        "description": f"Derivative of {equation}"
    }

def solve_equation(state, equation, variable):

    expr = state["equations"][equation]["expression"]
    variable = Symbol(variable)

    solutions = solve(Eq(expr, 0), variable)

    if len(solutions) == 0:
        raise ValueError("No solution found.")

    if len(solutions) > 1:
        raise NotImplementedError(
            "Multiple solutions not yet supported."
        )

    result = Eq(variable, solutions[0])

    return {
        "expression": result,
        "type": "solution",
        "variable": str(variable),
        "parents": [equation],
        "generated_by": "solve",
        "description": f"Solution of {equation}"
    }

def simplify_expression(state, equation):

    expr = state["equations"][equation]["expression"]

    result = simplify(expr)

    return {
        "expression": result,
        "type": state["equations"][equation]["type"],
        "variable": state["equations"][equation]["variable"],
        "parents": [equation],
        "generated_by": "simplify",
        "description": f"Simplified {equation}"
    }

def substitute(state, target_eq, substitution_eq):

    target = state["equations"][target_eq]["expression"]
    substitution = state["equations"][substitution_eq]["expression"]

    # Convert solve() output to Eq if necessary
    if isinstance(substitution, list):

        variable = Symbol(state["equations"][substitution_eq]["variable"])

        if len(substitution) != 1:
            raise NotImplementedError(
                "Multiple solutions not yet supported."
            )

        substitution = Eq(variable, substitution[0])

    if not isinstance(substitution, Eq):
        raise ValueError(
            "Substitution node must contain a SymPy Eq object."
        )

    result = target.subs(
        substitution.lhs,
        substitution.rhs
    )

    return {
        "expression": result,
        "type": "expression",
        "parents": [target_eq, substitution_eq],
        "generated_by": "substitute",
        "description": f"Substitute {substitution_eq} into {target_eq}"
    }

def estimate_parameters(state,model_id):
    model = state["equations"][model_id]

    dataset = state["equations"][model["parents"][0]]

    fitted_expression = fit(model["expression"], model["parameters"], model["independent_variables"],
            model["dependent_variables"], model["observations"])
    fit(
        model["expression"],
        model["parameters"],
        dataset["expression"]["observations"]
    )

    return {

        "expression": fitted_expression,

        "object_type": "function",

        "parents":[model_id],

        "generated_by":"EstimateParameters"
    }


OPERATIONS = {

    "differentiate": {
        "inputs": 1,
        "executor": differentiate
    },

    "solve": {
        "inputs": 1,
        "executor": solve_equation
    },

    "simplify": {
        "inputs": 1,
        "executor": simplify_expression
    },

    "substitute": {
        "inputs": 2,
        "executor": substitute
    },

    "EstimateParameters": {

        "executor": estimate_parameters
    }
}
