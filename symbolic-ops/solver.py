from sympy import *
from llama_cpp import Llama, LlamaGrammar
import json
from stock_operations import *
from goal_specification import *

TOOLS = ["differentiate","integrate","expand","factor","simplify","substitute","solve","finish"]

x = symbols('x')

def get_new_equation_id(state):
    existing = state["equations"].keys()
    print(f" Existing eq_ids: {existing}")

    numbers = [int(name.replace("eq", "")) for name in existing if name.startswith("eq")]

    return f"eq{max(numbers)+1}"

def state_to_prompt(state):
    text = ""

    text += f"Goal:\n{state['goal']}\n\n"

    text += "Known equations:\n"

    for name, data in state["equations"].items():
        text += f"""
            {name}:
              expression: {data['expression']}
              type: {data['type']}
              description: {data['description']}
            """

        if "parents" in data:
            text += f"  derived from: {data['parents']}\n"

    return text

state_trajectory = {

    "goal": "Given a set of points in a plane over time (x,y,t), find the trajectory function that best describes the particle's movement",

    "equations": {

        "obs1": {

            "expression": observations,

            "type": "dataset",

            "object_type": "dataset",

            "description": "Projectile measurements"
        }
    }
}

state = {
    "goal": "Find the stationary points of x**2 + 2*x + 1",
    "equations": {
        "eq1": {
            "expression": x**2+2*x+1,
            "type": "function",
            "variable": "x",
            "description": "quadratic polynomial"
        }
    }
}


def create_prompt(state):
    return f"""
        You are a scientific planning agent.

        Your task is to decide the next mathematical operation that moves
        closer to the goal.

        You have access to symbolic tools:

        differentiate
        simplify
        solve
        finish

        But also to the generation of hypothesis (model with parameters):
        GenerateModel
        and to model fitting (model with numbers):
        EstimateParameters

        Current scientific state:

        {state_to_prompt(state)}

        Choose the next action.
        """

def is_duplicate_expression(state, expression):
    for node in state["equations"].values():
        other = node["expression"]

        # Different object types -> definitely different
        if type(other) is not type(expression):
            continue

        if isinstance(expression, Equality):
            if (simplify(expression.lhs - other.lhs) == 0 and
                simplify(expression.rhs - other.rhs) == 0):
                return True

            # Optional: consider Eq(a,b) == Eq(b,a)
            if (simplify(expression.lhs - other.rhs) == 0 and
                simplify(expression.rhs - other.lhs) == 0):
                return True

        else:
            if simplify(other - expression) == 0:
                return True

    return False

def create_action_grammar(state):

    available_actions = []

    for eq_id, eq in state["equations"].items():

        # --------------------------
        # GenerateModel
        # --------------------------

        if eq["type"] == "dataset":

            for model_name in MODEL_LIBRARY.keys():

                already_attempted = any(
                    node.get("generated_by") == "GenerateModel"
                    and eq_id in node.get("parents", [])
                    and node.get("model_family") == model_name
                    for node in state["equations"].values()
                )

                if not already_attempted:

                    available_actions.append(
                        f"GenerateModel {eq_id} {model_name}"
                    )

        # --------------------------
        # EstimateParameters
        # --------------------------

        if eq["type"] == "model":

            already_fitted = any(
                node.get("generated_by") == "EstimateParameters"
                and eq_id in node.get("parents", [])
                for node in state["equations"].values()
            )

            if not already_fitted:

                dataset = eq["parents"][0]

                available_actions.append(
                    f"EstimateParameters {eq_id} {dataset}"
                )

        # --------------------------
        # Existing symbolic actions
        # --------------------------


        if eq["type"] == "solution":
            continue

        # 1. Differentiate functions
        if eq["type"] == "function":
            # If node is a function and is parent of a differentiated child, dont add to available actions
            already_done = any(
                node.get("generated_by") == "differentiate" and eq_id in node.get("parents", [])
                    for node in state["equations"].values())

            if not already_done:
                available_actions.append(f"differentiate {eq_id} {eq['variable']}")


        # 2. Solve derivatives
        if eq["type"] == "derivative":
            # If node is a derivative and is parent of a solved child, dont add solve to available actions
            already_done = any(
                node.get("generated_by") == "solve"and eq_id in node.get("parents", [])
                    for node in state["equations"].values())

            if not already_done:
                available_actions.append(
                    f"solve {eq_id} {eq['variable']}")


        # 3. Simplify anything
        if eq["type"] in ["function", "derivative"]:

            already_done = any(
                node.get("generated_by") == "simplify"and eq_id in node.get("parents", [])
                    for node in state["equations"].values())

            if not already_done:
                available_actions.append(f"simplify {eq_id}")


    action_rules = " | ".join(f'"{action}"'for action in available_actions)

    grammar = f'''
        root ::= action

        action ::= {action_rules}
        '''

    print(f"available_actions: {available_actions}")

    return LlamaGrammar.from_string(grammar)



"""
#########################################
"""

llm = Llama(model_path=r"C:\Users\PC\Documents\Github-RAG\qwen2.5-coder-7b-instruct-q4_k_m-00001-of-00002.gguf",n_ctx=2048,n_threads=8, verbose=False)
existing_eqs = []

from goal_compiler import compile_goal

print(state_trajectory['goal'])
goal_specification = compile_goal(f"{state_trajectory['goal']}\n\n", llm)
print(goal_specification)

while True:

    solved = False

    """ Return nodes with the expected solution type (number or function etc.) """
    candidates = CandidateExtractor.extract(state_trajectory,goal_specification.object_type)

    for candidate in candidates:
        all_success = True
        total_score = 0

        for condition in goal_specification.conditions:
            success, score = condition.evaluate(candidate,state_trajectory)

            all_success &= success
            total_score += score

        if all_success:
            print("SOLUTION")
            print(candidate)
            solved = True
            break
    if solved:
        break



    prompt = create_prompt(state_trajectory)
    grammar = create_action_grammar(state_trajectory)

    response = llm(
        prompt,
        max_tokens=64,
        temperature=0,
        grammar=grammar
    )

    if len(response["choices"][0]["text"].split()) == 3:
        tool, equation, variable = response["choices"][0]["text"].split()
    else:
        tool, equation = response["choices"][0]["text"].split()

    if tool in OPERATIONS:

        executor = OPERATIONS[tool]["executor"]

        if tool in ["differentiate", "solve"]:
            new_node = executor(
                state_trajectory,
                equation,
                variable
            )

        elif tool == "simplify":
            new_node = executor(
                state_trajectory,
                equation
            )

        if not is_duplicate_expression(state_trajectory, new_node["expression"]):
            new_id = get_new_equation_id(state_trajectory)
            state_trajectory["equations"][new_id] = new_node



"""
#########################################
"""

llm = Llama(model_path=r"C:\Users\PC\Documents\Github-RAG\qwen2.5-coder-7b-instruct-q4_k_m-00001-of-00002.gguf",n_ctx=2048,n_threads=8, verbose=False)
existing_eqs = []

from goal_compiler import compile_goal

goal_specification = compile_goal(f"{state['goal']}\n\n", llm)


while True:

    solved = False

    """ Return nodes with the expected solution type (number or function etc.) """
    candidates = CandidateExtractor.extract(state,goal_specification.object_type)

    for candidate in candidates:
        all_success = True
        total_score = 0

        for condition in goal_specification.conditions:
            success, score = condition.evaluate(candidate,state)

            all_success &= success
            total_score += score

        if all_success:
            print("SOLUTION")
            print(candidate)
            solved = True
            break
    if solved:
        break



    prompt = create_prompt(state)
    grammar = create_action_grammar(state)

    response = llm(
        prompt,
        max_tokens=64,
        temperature=0,
        grammar=grammar
    )

    if len(response["choices"][0]["text"].split()) == 3:
        tool, equation, variable = response["choices"][0]["text"].split()
    else:
        tool, equation = response["choices"][0]["text"].split()

    if tool in OPERATIONS:

        executor = OPERATIONS[tool]["executor"]

        if tool in ["differentiate", "solve"]:
            new_node = executor(
                state,
                equation,
                variable
            )

        elif tool == "simplify":
            new_node = executor(
                state,
                equation
            )

        if not is_duplicate_expression(state, new_node["expression"]):
            new_id = get_new_equation_id(state)
            state["equations"][new_id] = new_node
