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

class GoalSpecification:

    def __init__(self, object_type, conditions, constraints):
        self.object_type = object_type
        self.conditions = conditions
        self.constraints = constraints


class CandidateExtractor:

    @staticmethod
    def extract(state, object_type):

        candidates = []

        for eq_id, node in state.items():

            if object_type == "number":

                if node["type"] == "solution":

                    candidates.append(
                        {
                            "id": eq_id,
                            "node": node
                        }
                    )

            elif object_type == "function":

                if node["type"] == "function":

                    candidates.append(
                        {
                            "id": eq_id,
                            "node": node
                        }
                    )

            elif object_type == "equation":

                candidates.append(
                    {
                        "id": eq_id,
                        "node": node
                    }
                )

        return candidates
