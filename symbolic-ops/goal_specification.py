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


    def evaluate(self, state):

        candidates = find_candidates(
            state,
            self.object_type
        )

        best_score = float("inf")
        best_candidate = None

        for candidate in candidates:

            total_score = 0
            success = True

            for condition in self.conditions:

                ok, score = condition.evaluate(
                    candidate,
                    state
                )

                success &= ok
                total_score += score


            if total_score < best_score:
                best_score = total_score
                best_candidate = candidate


            if success:
                return GoalResult(
                    True,
                    candidate,
                    0
                )


        return GoalResult(
            False,
            best_candidate,
            best_score
        )
