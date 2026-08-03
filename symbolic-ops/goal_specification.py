from sympy import *
from llama_cpp import Llama, LlamaGrammar
import json
from stock_operations import *
from dataclasses import dataclass

"""
Given measurements (t_i,x_i,y_i), find the trajectory.

becomes:

GoalSpecification(
    object_type="function",
    object_symbol=["x(t)", "y(t)"],
    condition=[
        Eq(x(t_i), x_i),
        Eq(y(t_i), y_i)
    ],
    constraints=[
        t > 0
    ],
    verification_range={
        "t": (0,10)
    }
)

)
"""


@dataclass
class GoalSpecification:

    object_type: str

    conditions: list

    constraints: list
