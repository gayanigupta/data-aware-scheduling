#!/usr/bin/env python3
"""Task 2 -- MILP solver details for every MILP run in the paper.

For each experiment point (deadline slack, federation size, workflow
size, task failures, link bandwidth -- every setting and every one of the
five repetitions) and each per-dataset test run, this script rebuilds the
exact instance, builds the MILP, solves it, and records:

    number of variables, number of constraints, solver status,
    run time (s), optimality gap

Runs that were certified at the longer limit in task-01 are re-solved
with those settings (300 s, mip_rel_gap=1e-6); all other runs use the
first-pass settings (60 s, mip_rel_gap=1e-4). Runs skipped by the
n*m <= 800 assignment-variable cap are listed with their model size and
status 'skipped (cap)' -- no solve is attempted.

Output: revisions/results/task-02/milp_solver_details.csv

Run from the repo root:  python3 revisions/milp_solver_report.py
"""

import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
from scipy.optimize import milp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))
from fogsim import generate_instance
from fogsim.milp import _build_lp

OUT_DIR = os.path.join(os.path.dirname(__file__), "results", "task-02")
MILP_CAP = 800                      # n*m assignment-variable cap

GRIDS = {
    "slack":     [1.0, 1.2, 1.3, 1.5, 2.0],
    "nodes":     [2, 4, 6, 8, 10],
    "size":      [10, 100, 1000],
    "failure":   [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
    "bandwidth": [1.0, 0.5, 0.2, 0.1, 0.05],
}

# runs certified at the longer limit in task-01 (see fix_flagged_milp.py)
CERTIFIED = {
    ("slack", 1.2, 2), ("slack", 1.2, 3), ("slack", 1.2, 4),
    ("slack", 1.3, 3), ("slack", 1.5, 1),
    ("nodes", 10, 0), ("nodes", 10, 3),
    ("size", 100, 4),
    ("failure", 0.0, 1), ("failure", 0.1, 1), ("failure", 0.2, 1),
    ("failure", 0.3, 1), ("failure", 0.4, 1), ("failure", 0.5, 1),
    ("bandwidth", 1.0, 1), ("bandwidth", 0.2, 4),
}

TEST_DATASETS = [
    ("small",  dict(n_tasks=10,   n_nodes=3,  alpha=1.2, density=0.15, seed=0)),
    ("medium", dict(n_tasks=100,  n_nodes=5,  alpha=1.5, density=0.15, seed=1)),
    ("large",  dict(n_tasks=500,  n_nodes=8,  alpha=1.5, density=0.02, seed=2)),
    ("xlarge", dict(n_tasks=1000, n_nodes=10, alpha=1.5, density=0.02, seed=3)),
]


def rebuild(kind, param, rep):
    """Same instance generation as experiments.sweep()."""
    seed = 1000 * rep
    if kind == "slack":
        return generate_instance(n_tasks=50, n_nodes=5, alpha=param,
                                 seed=seed)
    if kind == "nodes":
        return generate_instance(n_tasks=50, n_nodes=int(param),
                                 alpha=1.5, seed=seed)
    if kind == "size":
        return generate_instance(n_tasks=int(param), n_nodes=5,
                                 alpha=1.5, density=0.05, seed=seed)
    inst = generate_instance(n_tasks=50, n_nodes=5, alpha=1.5, seed=seed)
    if kind == "bandwidth":
        off = ~np.eye(inst.m, dtype=bool)
        inst.B[off] *= param
    return inst


def model_size(inst):
    """Variable and constraint counts of the MILP, without solving."""
    n, m = inst.n, inst.m
    nvars = 2 * n * m + n                      # e, l, y
    ncons = n + n * m + m * sum(len(p) for p in inst.preds)
    return nvars, ncons


def solve(inst, time_limit, rel_gap):
    """Return (status_text, wall_s, mip_gap)."""
    c, con, bounds, nv, _ = _build_lp(inst)
    integ = np.zeros(nv)
    integ[: inst.n * inst.m] = 1.0
    t0 = time.time()
    res = milp(c, constraints=con, integrality=integ, bounds=bounds,
               options={"time_limit": time_limit, "mip_rel_gap": rel_gap})
    wall = time.time() - t0
    status = {0: "optimal", 1: "time limit", 2: "infeasible",
              3: "infeasible or unbounded"}.get(res.status,
                                                f"status {res.status}")
    gap = getattr(res, "mip_gap", np.nan)
    return status, wall, gap


def instance_key(inst):
    return (tuple(np.sort(inst.A).round(9)),
            tuple(inst.B.flatten().round(9)),
            round(inst.t_max, 9))


# ---------------------------------------------------------------- jobs
# One job per CSV row; solves are deduplicated across rows that share a
# generated instance (e.g. the failure experiment reuses one instance per
# repetition, and the default instance appears in three experiments).
jobs = []
for kind, params in GRIDS.items():
    for p in params:
        for rep in range(5):
            jobs.append(dict(experiment=kind, param=p, rep=rep,
                             seed=1000 * rep))
for name, kw in TEST_DATASETS:
    jobs.append(dict(experiment="test_run", param=name, rep="-",
                     seed=kw["seed"], test_kw=kw))

instances = {}     # key -> Instance
results = {}       # key -> (status, wall, gap)
pending = []       # jobs needing a solve


def get_inst(job):
    if "test_kw" in job:
        inst = generate_instance(**job["test_kw"])
    else:
        inst = rebuild(job["experiment"], job["param"], job["rep"])
    return inst


for job in jobs:
    inst = get_inst(job)
    key = instance_key(inst)
    job["key"] = key
    job["inst"] = inst
    if key not in instances:
        instances[key] = inst
        job["unique"] = True
        pending.append(job)
    else:
        job["unique"] = False


def run(job):
    inst = job["inst"]
    nvars, ncons = model_size(inst)
    key = job["key"]
    if inst.n * inst.m > MILP_CAP:
        return key, ("skipped (cap)", np.nan, np.nan, nvars, ncons,
                     np.nan, np.nan)
    flagged = (job["experiment"], job["param"], job["rep"]) in CERTIFIED
    limit, gap_tol = (300.0, 1e-6) if flagged else (60.0, 1e-4)
    status, wall, gap = solve(inst, limit, gap_tol)
    return key, (status, wall, gap, nvars, ncons, limit, gap_tol)


os.makedirs(OUT_DIR, exist_ok=True)
with ThreadPoolExecutor(max_workers=8) as ex:
    for key, out in ex.map(run, pending):
        results[key] = out
        print(f"{out[0]:>14s}  nvars={out[3]:>6d}  ncons={out[4]:>6d}  "
              f"wall={out[1] if out[1] == out[1] else -1:8.1f}s  "
              f"gap={out[2]}", flush=True)

rows = []
for job in jobs:
    status, wall, gap, nvars, ncons, limit, gtol = results[job["key"]]
    rows.append(dict(experiment=job["experiment"], param=job["param"],
                     rep=job["rep"], seed=job["seed"],
                     n_variables=nvars, n_constraints=ncons,
                     solver_status=status,
                     runtime_s=round(wall, 3) if wall == wall else "",
                     optimality_gap=round(gap, 6) if gap == gap else "",
                     time_limit_s=limit, rel_gap=gtol))

df = pd.DataFrame(rows)
out_csv = os.path.join(OUT_DIR, "milp_solver_details.csv")
df.to_csv(out_csv, index=False)
print(f"\nwrote {out_csv}  ({len(df)} rows, {len(instances)} unique "
      f"instances solved)")
