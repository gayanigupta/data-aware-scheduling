#!/usr/bin/env python3
"""Task 7 -- reproducibility: run every experiment under TWO independent
seed sets and check that the conclusions survive.

Set A uses seed base 0 (the paper's original seeds); set B uses seed base
7777 -- completely fresh instances.  Each set contributes 5 reps per
point; the merged CSVs (10 reps per point) replace data/results/*.csv,
and this script writes a per-point comparison of the two sets' mean
scores so we can show the results are not an artifact of one seed
choice.

Outputs:
    data/results/<kind>.csv                     merged 10-rep results
    revisions/results/task-07/reproduction_check.csv
Run from the repo root:  python3 revisions/run_reproduction.py
"""

import os
import shutil
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..")
RES = os.path.join(ROOT, "data", "results")
OUT = os.path.join(HERE, "results", "task-07")
sys.path.insert(0, os.path.join(ROOT, "code"))
from fogsim import experiment

KINDS = ["slack", "nodes", "size", "failure", "bandwidth"]
SEED_B = 7777
REPS = 5

os.makedirs(OUT, exist_ok=True)
setA = os.path.join(OUT, "setA")
setB = os.path.join(OUT, "setB")
os.makedirs(setA, exist_ok=True)
os.makedirs(setB, exist_ok=True)

# ---- set A: original seed base -------------------------------------------------
for k in KINDS:
    print(f"=== set A: {k}")
    experiment(k, seed=0)
    shutil.copy(os.path.join(RES, f"{k}.csv"),
                os.path.join(setA, f"{k}.csv"))

# ---- set B: independent seed base ----------------------------------------------
for k in KINDS:
    print(f"=== set B: {k}")
    experiment(k, seed=SEED_B)
    shutil.copy(os.path.join(RES, f"{k}.csv"),
                os.path.join(setB, f"{k}.csv"))

# ---- merge to 10 reps per point -------------------------------------------------
checks = []
for k in KINDS:
    a = pd.read_csv(os.path.join(setA, f"{k}.csv"))
    b = pd.read_csv(os.path.join(setB, f"{k}.csv"))
    b["rep"] = b["rep"] + REPS
    merged = pd.concat([a, b], ignore_index=True)
    merged.to_csv(os.path.join(RES, f"{k}.csv"), index=False)

    # compare set means per (param, method): does the ordering/score hold?
    for (p, m), ga in a.groupby(["param", "method"]):
        gb = b[(b["param"] == p) & (b["method"] == m)]
        if gb.empty:
            continue
        sa, sb = ga["score"].mean(), gb["score"].mean()
        fa, fb = ga["feasible"].mean(), gb["feasible"].mean()
        checks.append(dict(experiment=k, param=p, method=m,
                           score_setA=sa, score_setB=sb,
                           score_diff=abs(sa - sb),
                           feas_setA=fa, feas_setB=fb,
                           feas_diff=abs(fa - fb)))

chk = pd.DataFrame(checks)
chk.to_csv(os.path.join(OUT, "reproduction_check.csv"), index=False)
print("wrote", os.path.join(OUT, "reproduction_check.csv"))
print(f"max |score difference| between seed sets: "
      f"{chk['score_diff'].max():.3f}")
print(f"max |feasibility difference|: {chk['feas_diff'].max():.3f}")
