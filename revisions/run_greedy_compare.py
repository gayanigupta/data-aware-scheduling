#!/usr/bin/env python3
"""Compare uniform-fraction greedy vs critical-path greedy on the
same instances used for the tight-deadline experiment."""
import os, sys, time
import numpy as np
import pandas as pd

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "results", "2026-11-12")
sys.path.insert(0, os.path.join(HERE, "..", "code"))
from fogsim import generate_instance
from fogsim.experiments import evaluate

ALPHAS = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.5]
rows = []
for n in (10, 100):
    for a in ALPHAS:
        for rep in range(5):
            for base in (0, 7777):
                seed = base + 1000 * rep
                inst = generate_instance(n_tasks=n, n_nodes=5,
                                         alpha=a, seed=seed)
                bound = inst.score(np.ones(inst.n))
                for meth in ("greedy", "greedy_cp"):
                    r = evaluate(inst, meth, seed=seed)
                    rows.append(dict(n_tasks=n, alpha=a, rep=rep,
                                     seed_set="A" if base == 0 else "B",
                                     method=meth, bound=bound, **r))
df = pd.DataFrame(rows)
df.to_csv(os.path.join(OUT, "greedy_compare.csv"), index=False)

summ = (df.assign(ratio=df.score / df.bound)
          .groupby(["n_tasks", "alpha", "method"])
          .agg(score=("score", "mean"), ratio=("ratio", "mean"),
               deadline_met=("feasible", "mean"))
          .round(3).reset_index())
piv = summ.pivot_table(index=["n_tasks", "alpha"], columns="method",
                       values=["score", "ratio", "deadline_met"])
print(piv.to_string())
summ.to_csv(os.path.join(OUT, "greedy_compare_summary.csv"), index=False)
print("wrote", os.path.join(OUT, "greedy_compare.csv"))
