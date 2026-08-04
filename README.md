# A symbolic reasoner for physics problems
### Motivation
Current one-shot LLMs can assist scientists by generating explanations, code, or mathematical derivations. However, due to their token-by-token generating nature, they are fundamentally limited as autonomous research systems: they may rely on memorized knowledge, produce algebraic errors, cite unreliable literature, and cannot systematically verify or refine their own hypotheses through experimentation.

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

### Techniques: Knowledge Graphs

AI-4-Science decomposes scientific information into knowledge nodes, containing a mathematical function, equation, dataset, numerical value, hypothesis, or observation—together with its semantic type and provenance.

For example:

```
eq1 = {
    "expression": x**2 + 2*x + 1,
    "type": "function",
    "variable": "x",
    "description": "Quadratic polynomial",
    "parents": None
}
```

The graph explicitly stores how knowledge is generated. Every newly created node records which previous nodes produced it and which symbolic operation was applied. This allows every reasoning step to be inspected, verified, or reproduced.

### Symbolic Planning

Rather than asking an LLM to directly solve mathematical problems, the LLM only decides which symbolic operation should be performed next.

The actual mathematics is executed by deterministic symbolic tools such as

- Differentiate
- Simplify
- Solve
- Fit
- Integrate
...

For example, given the problem

> Find the stationary points of \(x^2 + 2x + 1\)

the planner generates the sequence

```
differentiate(eq1)

↓

solve(eq2)

↓

finish
```

while the symbolic engine performs every computation exactly.

This separates planning from execution, making every reasoning step transparent and verifiable.

### Knowledge Graph Search

Solving scientific problems can be viewed as searching through a graph of possible knowledge transformations.

Each symbolic operation expands the graph by generating new knowledge nodes. Most possible transformations are either redundant or irrelevant. The role of the planner is therefore not to perform mathematics, but to navigate efficiently through this enormous search space.

Current optimizations include

- goal-aware expansion,
- duplicate pruning,
- symbolic verification,
- explicit provenance tracking.

The same search framework naturally applies to

- symbolic deduction,
- hypothesis generation,
- equation discovery,
- scientific workflows.
### Roadmap

Problem solving and scientific discovery are fundamentally the same search process.

The difference is that in open-ended discovery the target is unknown. Instead of searching for a predefined answer, the system searches for hypotheses that best explain observations.

Ultimately, every scientific theory is evaluated against reality. Observations therefore act as the objective ground truth that guides exploration through the hypothesis space.

The long-term objective is to train the planner to make increasingly effective research decisions by maximizing criteria such as

1. predictive power,
2. simplicity and compression,
3. generality,
4. novelty,
5. precision.

Current roadmap:

- Symbolic reasoner for mathematical and physics problems.
- Support observational datasets as first-class knowledge nodes.
- Rediscover known physical laws from observations.
- Integrate literature retrieval through a RAG pipeline.
- Combine literature, symbolic reasoning and simulations into a closed-loop scientific agent.
- Explore autonomous scientific discovery.
### Scope of this Repository

The symbolic reasoner maintains an extensible library of mathematical transformations. The same reasoning engine is intended to solve both deductive and inductive scientific problems.

Examples include

Deduction

> Find the stationary points of \(x^2 + 2x + 1\)

Induction

> Given noisy observations of a trajectory \( (t,x,y) \) infer the mathematical model that best explains the data.

The long-term vision is that both tasks are instances of the same underlying problem:

> Search through the space of symbolic knowledge transformations until the generated theory best explains the available evidence.
