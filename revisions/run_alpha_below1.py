#!/usr/bin/env python3
"""Tight-deadline experiment (alpha < 1.0): partial execution is forced.

Run all four methods on 10-task and 100-task instances at alpha in
{0.5,0.6,0.7,0.8,0.9,1.0,1.2,1.5}, 5 replications per point, merged with
a second seed set (7777) -> 10 reps.  Output goes to
revisions/results/2026-11-12/.
"""

import os, sys, time
import numpy as np
import pandas as pd

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(HERE, "results", "2026-11-12")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(ROOT, "code"))
from fogsim import generate_instance
from fogsim.experiments import evaluate

ALPHAS = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.5]
SIZES  = [10, 100]
METHODS = ["milp", "rounding", "greedy", "ga"]

rows = []
for n in SIZES:
    for a in ALPHAS:
        for rep in range(5):
            for base in (0, 7777):
                seed = base + 1000 * rep
                inst = generate_instance(n_tasks=n, n_nodes=5,
                                         alpha=a, seed=seed)
                bound = inst.score(np.ones(inst.n))
                for meth in METHODS:
                    if meth == "milp" and inst.n * inst.m > 800:
                        continue
                    trials = max(4, min(40, 20000 // (inst.n * inst.m)))
                    t0 = time.time()
                    r = evaluate(inst, meth, seed=seed, trials=trials)
                    rows.append(dict(n_tasks=n, alpha=a, rep=rep,
                                     seed_set="A" if base == 0 else "B",
                                     method=meth, bound=bound, **r))
                    print(f"n={n} a={a} rep={rep} set={'A' if base==0 else 'B'} "
                          f"{meth}: score={r['score']:.3f} feas={r['feasible']:.0f} "
                          f"({time.time()-t0:.0f}s)", flush=True)

df = pd.DataFrame(rows)
out = os.path.join(OUT, "alpha_below1.csv")
df.to_csv(out, index=False)
print("wrote", out, len(df), "runs")
