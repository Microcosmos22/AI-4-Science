# A symbolic reasoner for physics problems
### Motivation
Using one-query-answer LLMs to perform research has the problem of memorized answers, algebraic errors, references to
poor literature, not to mention a lack of scientific curiosity and initiative.

Using LLMs for scientific planning, while outsourcing the algebra, literature retrieval and simulation design permits
continuous checking and improvement of hypothesis in so called closed-loop research.
The goal of AI-4-Science is to automate the complete research process just like a scientist would work, with the ultimate
goal to discover new fields of physics.

An example research process might look like:

```
Literature retrieval
|
New hypothesis from combination or analogy
|
Draw analytical conclusions / predict observation
|
Perform Python simulation
|
Theory imperfect, re-formulate better hypothesis from literature
```

### Techniques
In order for a computer to process scientific information, we separate each statement into minimal units of information,
called nodes. They contain a mathematical expression, the object type, its related nodes (parents) and some explanation:

```
"eq1": {
        "expression": x**2+2*x+1,
        "type": "function",
        "variable": "x",
        "description": "quadratic polynomial"
        }
```

We can transform this expression, combine it with others, to generate new knowledge. The graph containing all information 
and its relations is called a knowledge graph. This is an important piece of scientific discovery, responsible for induction
from experiments, deduction and scientific reasoning.

### Roadmap for the symbolic reasoner
One could argue that performing open-ended discovery differs from problem solving, where we know the correct direction
for the flow of knowledge. However we must not forget that at the end of every research we will always meet a ground
truth in the form of an observation of the real world. In open-ended research we deal with an enormous hypothesis space and 
should not brute-force all operations. The real challenge is to train our scientific planner to make useful progress,
make the right reseadecisions
