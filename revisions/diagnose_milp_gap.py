#!/usr/bin/env python3
"""Why does a heuristic sometimes beat the MILP?

For every sweep point where the greedy scored above the MILP, this script
rebuilds the exact same instance (same generator arguments and seed),
checks it really is the same instance by comparing the stored accuracy
bound, then reruns the MILP twice: once at the original 60-second limit
and once at 300 seconds. For each solve it prints the solver status, wall
time, MIP gap, and achieved score.

Run from the repo root:

    python3 revisions/diagnose_milp_gap.py
"""

import os
import sys
import time

import numpy as np
import pandas as pd
from scipy.optimize import milp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))
from fogsim import generate_instance
from fogsim.milp import _build_lp, _extract
from fogsim.greedy import run_greedy

RESULTS = os.path.join(os.path.dirname(__file__), "..", "data", "results")

# every (sweep, parameter, rep) where the greedy scored above the MILP
FLAGGED = [
    ("slack", 1.2, 2),
    ("slack", 1.2, 3),
    ("slack", 1.2, 4),
    ("slack", 1.3, 3),
    ("slack", 1.5, 1),   # same instance as failure rep 1 / bandwidth 1.0 rep 1
    ("nodes", 10, 0),
    ("nodes", 10, 3),
    ("size", 100, 4),
    ("bandwidth", 0.2, 4),
]


def rebuild(kind, param, rep):
    """Recreate the exact instance sweep() used for this point."""
    seed = 1000 * rep
    if kind == "slack":
        inst = generate_instance(n_tasks=50, n_nodes=5, alpha=param,
                                 seed=seed)
    elif kind == "nodes":
        inst = generate_instance(n_tasks=50, n_nodes=param, alpha=1.5,
                                 seed=seed)
    elif kind == "size":
        inst = generate_instance(n_tasks=param, n_nodes=5, alpha=1.5,
                                 density=0.05, seed=seed)
    else:  # failure and bandwidth use the default 50-task, 5-node instance
        inst = generate_instance(n_tasks=50, n_nodes=5, alpha=1.5,
                                 seed=seed)
        if kind == "bandwidth":
            off = ~np.eye(inst.m, dtype=bool)
            inst.B[off] *= param
    return inst, seed


def solve(inst, limit):
    """Run the MILP; return (status, wall seconds, gap, score)."""
    c, con, bounds, nv, _ = _build_lp(inst)
    integ = np.zeros(nv)
    integ[: inst.n * inst.m] = 1.0
    t0 = time.time()
    res = milp(c, constraints=con, integrality=integ, bounds=bounds,
               options={"time_limit": limit, "mip_rel_gap": 1e-4})
    wall = time.time() - t0
    if res.x is None:
        return res.status, wall, np.nan, np.nan
    assign, ell = _extract(res, inst)
    return res.status, wall, res.mip_gap, inst.score(ell)


rows = []
for kind, param, rep in FLAGGED:
    inst, seed = rebuild(kind, param, rep)
    bound = inst.score(np.ones(inst.n))

    # check it really is the same instance the sweep used
    csv = pd.read_csv(os.path.join(RESULTS, kind + ".csv"))
    stored = csv[(csv.param == param) & (csv.rep == rep)].bound.iloc[0]
    same = "SAME" if abs(bound - stored) < 1e-9 else "MISMATCH"

    greedy = run_greedy(inst)
    greedy_score = inst.score(greedy[1])

    s60 = solve(inst, 60.0)
    s300 = solve(inst, 300.0)

    print(f"{kind} p={param} rep={rep} (seed {seed}) [{same}]")
    print(f"   bound={bound:.4f}  greedy={greedy_score:.4f}")
    print(f"   60 s : status={s60[0]} wall={s60[1]:.1f}s "
          f"gap={s60[2]:.4g} score={s60[3]:.4f}")
    print(f"   300 s: status={s300[0]} wall={s300[1]:.1f}s "
          f"gap={s300[2]:.4g} score={s300[3]:.4f}\n")

    rows.append(dict(sweep=kind, param=param, rep=rep, seed=seed,
                     instance_check=same, bound=bound,
                     greedy=greedy_score,
                     milp60_status=s60[0], milp60_wall_s=round(s60[1], 1),
                     milp60_gap=s60[2], milp60_score=s60[3],
                     milp300_status=s300[0], milp300_wall_s=round(s300[1], 1),
                     milp300_gap=s300[2], milp300_score=s300[3]))

out = os.path.join(os.path.dirname(__file__), "milp_diagnostics.csv")
pd.DataFrame(rows).to_csv(out, index=False)
print("wrote", out)
