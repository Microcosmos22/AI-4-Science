# goal_compiler.py

import json

from goal_specification import GoalSpecification
from goal_conditions import (
    DerivativeEqualsZero,
    FitsMeasurements,
)
from llama_cpp import Llama, LlamaGrammar



# Registry of available goal conditions
CONDITION_CLASSES = {
    "DerivativeEqualsZero": DerivativeEqualsZero,
    "FitsMeasurements": FitsMeasurements,
}


GOALFINDER_PROMPT = """
You are a mathematical goal compiler.

Translate the problem statement into the goal specification language.

Output ONLY the goal specification.

The object_type describes the final answer that should be returned.

Rules:

- If the answer is a value, root, point, parameter, or coordinate, use:
number

- If the answer is an explicit mathematical expression depending on variables, use:
function

- If the answer is a relation or equation itself, use:
equation

Examples:

Problem:
Find the stationary points of f(x)

The answer is the x-values where the derivative is zero.

Output:
number;DerivativeEqualsZero(original_function);None


Problem:
Find the trajectory from measured points

The answer is a function x(t), y(t).

Output:
function;FitsMeasurements(observations);None


Problem:
Write the equation that defines the stationary points

The answer is the equation f'(x)=0.

Output:
equation;DerivativeEqualsZero(original_function);None
"""


grammar = LlamaGrammar.from_string(r"""
root ::= goal

goal ::= type ";" conditions ";" constraints

type ::= "number" | "function" | "matrix" | "equation"

conditions ::= condition ("," condition)*

condition ::= "DerivativeEqualsZero(" target ")" | "FitsMeasurements(" dataset ")"

target ::= "original_function"

dataset ::= "observations"

constraints ::= "None"
""")

def parse_goal(text):

    object_type, condition_text, constraint_text = text.split(";")

    conditions = []

    for c in condition_text.split(","):

        if c.startswith("DerivativeEqualsZero"):
            target = c.split("(")[1].split(")")[0]

            conditions.append(
                DerivativeEqualsZero(target)
            )

        elif c.startswith("FitsMeasurements"):
            dataset = c.split("(")[1].split(")")[0]

            conditions.append(
                FitsMeasurements(dataset)
            )


    constraints = []

    if constraint_text != "None":
        constraints.append(constraint_text)


    return GoalSpecification(
        object_type=object_type,
        conditions=conditions,
        constraints=constraints
    )

def compile_goal(problem_statement, llm):

    prompt = f"""
    Problem:

    {problem_statement}

    """

    print(GOALFINDER_PROMPT)
    print(prompt)

    response = llm.create_completion(
        GOALFINDER_PROMPT+prompt,
        grammar=grammar,
        max_tokens=50,
        temperature=0
    )
    response_text = response["choices"][0]["text"]

    print(response_text)

    return parse_goal(response_text)
