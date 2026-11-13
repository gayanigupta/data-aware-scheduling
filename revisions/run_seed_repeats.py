#!/usr/bin/env python3
"""Seed-repeat study: rounding and GA run 10x with seeds 0-9 on one
representative instance per (n, alpha) of the tight-deadline grid."""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "results", "2026-11-12")
sys.path.insert(0, os.path.join(HERE, "..", "code"))
from fogsim import generate_instance
from fogsim.experiments import evaluate

ALPHAS = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.5]
SEEDS = list(range(10))
rows = []
for n in (10, 100):
    for a in ALPHAS:
        inst = generate_instance(n_tasks=n, n_nodes=5, alpha=a, seed=0)
        bound = inst.score(np.ones(inst.n))
        for meth in ("rounding", "ga"):
            for s in SEEDS:
                trials = max(4, min(40, 20000 // (inst.n * inst.m)))
                r = evaluate(inst, meth, seed=s, trials=trials)
                rows.append(dict(n_tasks=n, alpha=a, method=meth,
                                 seed=s, bound=bound, **r))
                print(f"n={n} a={a} {meth} seed={s} "
                      f"score={r['score']:.3f} feas={r['feasible']}",
                      flush=True)
df = pd.DataFrame(rows)
df.to_csv(os.path.join(OUT, "seed_repeats.csv"), index=False)
summ = (df.assign(ratio=df.score/df.bound)
          .groupby(["n_tasks","alpha","method"])
          .agg(mean_ratio=("ratio","mean"), std_ratio=("ratio","std"),
               mean_score=("score","mean"), feas_rate=("feasible","mean"))
          .round(4).reset_index())
summ.to_csv(os.path.join(OUT, "seed_repeats_summary.csv"), index=False)
print(summ.to_string())
print("wrote", os.path.join(OUT, "seed_repeats.csv"))
