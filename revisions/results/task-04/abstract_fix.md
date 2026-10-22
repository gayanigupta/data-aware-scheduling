# Task 4 — Abstract wording fix

**Changed in:** `paper/main.tex`, abstract (line 53).

Before: "The data size on each edge, the bandwidth of each link, and the
execution fraction of each task are all modeled jointly in the
optimization" — this lumps fixed inputs together with decision
variables.

After: "The model takes the data size on each edge and the bandwidth of
each link as fixed inputs, and decides only where each task runs and how
much of it runs; to our knowledge, no earlier model treats these inputs
and decisions together."

Now only node placement and execution fraction are described as
decisions; data size and bandwidth are stated as inputs. The commented
contribution bullet (line 81) was updated to match.

Verification: `main.pdf` recompiles cleanly.
