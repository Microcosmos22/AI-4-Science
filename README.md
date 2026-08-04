# A symbolic reasoner for physics problems
### Motivation
Current one-shot LLMs can assist scientists by generating explanations, code, or mathematical derivations. However, they are fundamentally limited as autonomous research systems: they may rely on memorized knowledge, produce algebraic errors, cite unreliable literature, and cannot systematically verify or refine their own hypotheses through experimentation.

AI-4-Science approaches this problem differently. Instead of using an LLM as the reasoning engine, the LLM acts as a scientific planner that orchestrates specialized tools for **symbolic mathematics, literature retrieval, numerical simulation, and data analysis**. Each intermediate result is stored in a structured knowledge graph and can be independently verified, reused, or revised.

This architecture enables closed-loop scientific reasoning, where hypotheses are continuously generated, tested, and refined based on analytical results, simulations, and newly acquired knowledge.

The long-term goal is to automate the scientific discovery process itself—from literature exploration to hypothesis generation and experimental validation—with the eventual aim of discovering previously unknown physical laws.

An example closed-loop research process might look like:

```
Literature Retrieval
│
▼
Hypothesis Generation
│
▼
Symbolic Analysis / Mathematical Derivations
│
▼
Simulation or Experimental Prediction
│
▼
Compare with Observations
│
▼
Refine Hypothesis using New Evidence
│
└──────────────────────────────┐
                               ▼ Repeat until convergence
```

### Techniques: Knowledge-graphs
In order for a computer to process scientific information, we separate each statement into minimal units of information,
called nodes. They might contain a number, a function, an equation, a dataset etc. accompanied by the object type, its related nodes (parents) and some text-based explanation:

```
"eq1": {
        "expression": x**2+2*x+1,
        "type": "function",
        "variable": "x",
        "description": "quadratic polynomial"
        "parents": None
        }
```

We can transform or combine this information nodes to generate new knowledge. Applying the correct transformations, we are able to gain information or solve physics problems:
```
        You are a mathematical goal compiler.
        Translate the problem statement into the goal specification language.
        Problem:

            Find the stationary points of x**2 + 2*x + 1

GoalSpecification:
number;DerivativeEqualsZero(original_function);None
<goal_specification.GoalSpecification object at 0x00000233B415CEC0>

####################################################################################
KNOWLEDGE GRAPH - EXPLORATION OF HYPOTHESIS SPACE
(The correct solution path using knowledge tree, goal-aware expansion stop, pruning duplicate nodes etc.)


 You are a scientific planning agent.

        Your task is to decide the next mathematical operation that moves
        closer to the goal.

        You have access to symbolic tools:

        differentiate
        simplify
        solve
        finish

        Goal:
Find the stationary points of x**2 + 2*x + 1



            eq1:
              expression: x**2 + 2*x + 1
              type: function
              description: quadratic polynomial
differentiate eq1 x

            eq2:
              expression: 2*x + 2
              type: derivative
              description: Derivative of eq1
              derived from: ['eq1']
solve eq2 x
            eq3:
              expression: Eq(x, -1)
              type: solution
              description: Solution of eq2
              derived from: ['eq2']

GoalSpecification FOUND A SOLUTION
{'id': 'eq3', 'node': {'expression': Eq(x, -1), 'type': 'solution', 'variable': 'x', 'parents': ['eq2'], 'generated_by': 'solve', 'description': 'Solution of eq2'}}
```


The graph containing all nodes and the space of all actions that relate them, is a knowledge graph. This tree contains scientific discovery but also
an enourmous space of transformations that do not generate any new knowledge. When expanded in the right direction, the **symbolic solver is responsible for induction
from experiments, deduction and scientific reasoning**.

### Roadmap for the symbolic reasoner
One could argue that performing open-ended discovery differs from problem solving, where we know the correct direction
for the flow of knowledge. However we must not forget that at the end of every research we will always meet a ground
truth in the form of an observation of the real world. In open-ended research we deal with an enormous hypothesis space and should not brute-force all operations. The real challenge is to train our scientific planner to make useful progress, make the right research decisions. The main metrics for scientific progress are: Predictive power, Compression/simplicity, novelty, generality and precision, in descending order of importance.

We asked ChatGPT to make a roadmap for this project, including different milestones:
1. A symbolic reasoner that solves physics problems from equations.
2. Add observations datasets as inputs.
3. Re-discover known physics: Given equations prior to a discovery (prior to Newtons classical mechanics), recover known physics laws.
4. Implement literature: Using a RAG Agent, re-discover known physics using also the text contexts.
5. Novel scientific discovery multi-agent.

### Scope of this repository
The symbolic reasoner has an internal library of mathematical operations than span the space of possible actions. This will grow over time, but
we intend to solve two different problems using the same code (given to it as Text):
1. "Problem:

    Find the stationary points of x**2 + 2*x + 1"
2. "Given a noisy dataset of a trajectory in a plane $(t,x,y)_i$, find the equation of the objects trajectory that makes the best fit" (parabola/cannonball)


