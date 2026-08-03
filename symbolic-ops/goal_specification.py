from sympy import *
from llama_cpp import Llama, LlamaGrammar
import json
from stock_operations import *
from dataclasses import dataclass

"""
{
 "object_type": "number",
 "conditions": [
   {
     "type": "DerivativeEqualsZero",
     "target": "original_function"
   }
 ],
 "constraints": []
}
"""


@dataclass
class GoalSpecification:

    object_type: str

    conditions: list

    constraints: list
