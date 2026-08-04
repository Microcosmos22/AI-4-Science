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

grammar = LlamaGrammar.from_string(r'''
root ::= tool " " equation " " variable

tool ::= "differentiate"| "simplify"| "solve"

equation ::= "eq1"| "eq2"| "eq3"

variable ::= "x"| "y"| "z"
''')


def create_action_grammar(state):

    available_actions = []

    for eq_id, eq in state["equations"].items():

        if eq["type"] == "solution":
            continue

        # 1. Differentiate functions
        if eq["type"] == "function":

            already_done = any(
                node.get("generated_by") == "differentiate"
                and eq_id in node.get("parents", [])
                for node in state["equations"].values()
            )

            if not already_done:
                available_actions.append(
                    f"differentiate {eq_id} {eq['variable']}"
                )


        # 2. Solve derivatives
        if eq["type"] == "derivative":

            already_done = any(
                node.get("generated_by") == "solve"
                and eq_id in node.get("parents", [])
                for node in state["equations"].values()
            )

            if not already_done:
                available_actions.append(
                    f"solve {eq_id} {eq['variable']}"
                )


        # 3. Simplify anything
        if eq["type"] in ["function", "derivative"]:

            already_done = any(
                node.get("generated_by") == "simplify"
                and eq_id in node.get("parents", [])
                for node in state["equations"].values()
            )

            if not already_done:
                available_actions.append(
                    f"simplify {eq_id}"
                )


    action_rules = " | ".join(
        f'"{action}"'
        for action in available_actions
    )

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

goal_specification = compile_goal(f"{state['goal']}\n\n", llm)

print("GoalSpecification:")
print(goal_specification)
print("Lets do induction")

while True:
    print(f"\nState: {state}")
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
    print(prompt)

    response = llm(
        prompt,
        max_tokens=64,
        temperature=0,
        grammar=grammar
    )

    print(response["choices"][0]["text"])
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
