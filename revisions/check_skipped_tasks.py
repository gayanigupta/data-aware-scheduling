#!/usr/bin/env python3
"""Task 5 -- how often does the MILP actually skip a task (ell_i = 0)?

The model allows the execution fraction to be zero.  A task with
ell_i = 0 performs no work and earns no accuracy, yet its outgoing data
D_ji is still transferred to its successors.  Before deciding between
(a) enforcing a minimum fraction and (b) documenting the semantics, this
script measures how often skipped tasks occur in practice.

For every unique experiment instance (same rebuild logic and solver
settings as revisions/milp_solver_report.py) the MILP is solved, the
fraction vector is decoded, and the number of tasks with ell_i = 0 is
recorded together with the minimum and mean fraction.

Output: revisions/results/task-05/skipped_tasks.csv

Run from the repo root:  python3 revisions/check_skipped_tasks.py
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
from fogsim.milp import _build_lp, _extract

OUT_DIR = os.path.join(os.path.dirname(__file__), "results", "task-05")
TOL = 1e-6          # a task counts as skipped when ell_i < TOL
MILP_CAP = 800      # n*m assignment-variable cap, same as experiments

# --- experiment grids, copied from milp_solver_report.py so this script
# does not import it (that module executes its solves at import time) ---
GRIDS = {
    "slack":     [1.0, 1.2, 1.3, 1.5, 2.0],
    "nodes":     [2, 4, 6, 8, 10],
    "size":      [10, 100, 1000],
    "failure":   [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
    "bandwidth": [1.0, 0.5, 0.2, 0.1, 0.05],
}
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


def instance_key(inst):
    return (tuple(np.sort(inst.A).round(9)),
            tuple(inst.B.flatten().round(9)),
            round(inst.t_max, 9))

jobs = []
for kind, params in GRIDS.items():
    for p in params:
        for rep in range(5):
            jobs.append(dict(experiment=kind, param=p, rep=rep,
                             seed=1000 * rep))
for name, kw in TEST_DATASETS:
    jobs.append(dict(experiment="test_run", param=name, rep="-",
                     seed=kw["seed"], test_kw=kw))

seen = set()
pending = []
for job in jobs:
    if "test_kw" in job:
        inst = generate_instance(**job["test_kw"])
    else:
        inst = rebuild(job["experiment"], job["param"], job["rep"])
    key = instance_key(inst)
    job["key"] = key
    job["inst"] = inst
    if key not in seen:
        seen.add(key)
        job["unique"] = True
        pending.append(job)
    else:
        job["unique"] = False


def run(job):
    inst = job["inst"]
    if inst.n * inst.m > MILP_CAP:
        return job["key"], ("skipped (cap)", np.nan, np.nan, np.nan,
                            np.nan, "skipped (cap)")
    flagged = (job["experiment"], job["param"], job["rep"]) in CERTIFIED
    limit, gtol = (300.0, 1e-6) if flagged else (60.0, 1e-4)
    c, con, bounds, nv, _ = _build_lp(inst)
    integ = np.zeros(nv)
    integ[:inst.n * inst.m] = 1.0
    t0 = time.time()
    res = milp(c, constraints=con, integrality=integ, bounds=bounds,
               options={"time_limit": limit, "mip_rel_gap": gtol})
    wall = time.time() - t0
    status = {0: "optimal", 1: "time limit"}.get(res.status,
                                                 f"status {res.status}")
    if res.x is None:
        return job["key"], (status, wall, np.nan, np.nan, np.nan,
                            "no solution")
    _, ell = _extract(res, inst)
    return job["key"], (status, wall, int(np.sum(ell < TOL)),
                        float(ell.min()), float(ell.mean()), "ok")


os.makedirs(OUT_DIR, exist_ok=True)
results = {}
with ThreadPoolExecutor(max_workers=8) as ex:
    for key, out in ex.map(run, pending):
        results[key] = out
        print(f"{out[0]:>14s}  skipped={out[2]}  min={out[3]}  "
              f"mean={out[4]:.4f}" if out[4] == out[4]
              else f"{out[0]:>14s}", flush=True)

rows = []
for job in jobs:
    status, wall, nskip, emin, emean, note = results[job["key"]]
    rows.append(dict(experiment=job["experiment"], param=job["param"],
                     rep=job["rep"], seed=job["seed"],
                     solver_status=status, runtime_s=round(wall, 2),
                     n_tasks=job["inst"].n, n_skipped=nskip,
                     min_fraction=emin, mean_fraction=round(emean, 5)
                     if emean == emean else "", note=note))

df = pd.DataFrame(rows)
out_csv = os.path.join(OUT_DIR, "skipped_tasks.csv")
df.to_csv(out_csv, index=False)

solved = df[df["note"] == "ok"]
total_skip = solved["n_skipped"].sum()
total_tasks = solved["n_tasks"].sum()
print(f"\nwrote {out_csv} ({len(df)} rows)")
print(f"skipped tasks across all solved runs: {total_skip} / "
      f"{total_tasks} ({100.0 * total_skip / total_tasks:.2f}%)")
runs_with_skip = (solved["n_skipped"] > 0).sum()
print(f"runs containing at least one skipped task: {runs_with_skip} "
      f"/ {len(solved)}")
