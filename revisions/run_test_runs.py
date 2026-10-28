#!/usr/bin/env python3
"""Re-run the per-dataset test runs (paper Table II) with the current
instance generator.

Datasets mirror the notebook: small / medium / large / xlarge with fixed
seeds.  The MILP is skipped above 800 assignment variables (n*m) and
rounding is skipped on the two largest datasets, exactly as the table
caption states.  Results overwrite data/results/test_runs.csv.

Run from the repo root:  python3 revisions/run_test_runs.py
"""

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..")
RES = os.path.join(ROOT, "data", "results")
sys.path.insert(0, os.path.join(ROOT, "code"))

from fogsim import generate_instance
from fogsim.experiments import evaluate

TEST_DATASETS = [
    ("small",  dict(n_tasks=10,   n_nodes=3,  alpha=1.2, density=0.15, seed=0)),
    ("medium", dict(n_tasks=100,  n_nodes=5,  alpha=1.5, density=0.15, seed=1)),
    ("large",  dict(n_tasks=500,  n_nodes=8,  alpha=1.5, density=0.02, seed=2)),
    ("xlarge", dict(n_tasks=1000, n_nodes=10, alpha=1.5, density=0.02, seed=3)),
]

MILP_CAP = 800

rows = []
for name, kw in TEST_DATASETS:
    inst = generate_instance(**kw)
    bound = inst.score(np.ones(inst.n))
    for meth in ["milp", "rounding", "greedy", "ga"]:
        if meth == "milp" and inst.n * inst.m > MILP_CAP:
            rows.append(dict(dataset=name, method=meth, score=np.nan,
                             makespan=np.nan, feasible=np.nan,
                             runtime_s=np.nan))
            continue
        if meth == "rounding" and name in ("large", "xlarge"):
            rows.append(dict(dataset=name, method=meth, score=np.nan,
                             makespan=np.nan, feasible=np.nan,
                             runtime_s=np.nan))
            continue
        trials = max(4, min(40, 20000 // (inst.n * inst.m)))
        r = evaluate(inst, meth, seed=kw["seed"], trials=trials)
        rows.append(dict(dataset=name, method=meth, **r))
        print(f"{name} {meth}: score={r['score']:.3f} "
              f"feas={r['feasible']} ({r['runtime_s']:.1f}s)  bound={bound:.3f}")

df = pd.DataFrame(rows)
out = os.path.join(RES, "test_runs.csv")
df.to_csv(out, index=False)
print("wrote", out)
