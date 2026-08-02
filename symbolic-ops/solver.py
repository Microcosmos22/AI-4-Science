from sympy import *
from llama_cpp import Llama, LlamaGrammar
import json

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

grammar = LlamaGrammar.from_string(r'''
root ::= tool " " equation " " variable

tool ::= "differentiate"| "simplify"| "solve"

equation ::= "eq1"| "eq2"| "eq3"

variable ::= "x"| "y"| "z"
''')


def create_action_grammar(state):

    available_actions = []

    for eq_id, eq in state["equations"].items():

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




llm = Llama(model_path=r"C:\Users\PC\Documents\Github-RAG\qwen2.5-coder-7b-instruct-q4_k_m-00001-of-00002.gguf",n_ctx=2048,n_threads=8, verbose=False)
existing_eqs = []

while True:
    print(f"\nState: {state}")

    prompt = create_prompt(state)
    grammar = create_action_grammar(state)

    response = llm(
        prompt,
        max_tokens=64,
        temperature=0,
        grammar=grammar
    )

    print(response["choices"][0]["text"])
    tool, equation, variable = response["choices"][0]["text"].split()


    if tool == "differentiate":
        variable = Symbol(variable)
        result = diff(state["equations"][equation]["expression"], variable)

        new_id = get_new_equation_id(state)


        state["equations"][new_id] = {
            "expression": result,
            "type": "derivative",
            "variable": str(variable),
            "parents": [equation],
            "generated_by": "differentiate",
            "description": f"Derivative of {equation}"
        }
    elif tool == "solve":
        variable = Symbol(variable)
        eq = state["equations"][equation]["expression"]

        result = solve(Eq(eq,0), x)

        new_id = get_new_equation_id(state)

        state["equations"][new_id] = {
            "expression": result,
            "type": "derivative",
            "variable": str(variable),
            "parents": [equation],
            "generated_by": "differentiate",
            "description": f"Derivative of {equation}"
        }
