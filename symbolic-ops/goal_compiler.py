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
Given the problem statement, find a characterization for the expected solution in the following format:

object_type;condition;domain

Explanation/Rules:
1. What set is the solution expected to be in? (object_type)
Options: number, function, equation, matrix

2. What conditions must that solution object satisfy? (condition)
Options: FitsMeasurements, DerivativeEqualsZero

3. In which range/domain must that condition be satisfied in? (domain)
Options: None

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
    Problem statement:

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

    # returns a GoalSpecification
    return parse_goal(response_text)
