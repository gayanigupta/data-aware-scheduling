"""Experiment driver: per-run evaluation, the four sweeps of Section VI,
and the result figures.
"""

import os
import time

import numpy as np
import pandas as pd

from . import RES_DIR, FIG_DIR
from .instance import generate_instance
from .milp import run_milp
from .rounding import run_rounding
from .greedy import run_greedy
from .ga import run_ga

METHODS = {"milp": run_milp, "rounding": run_rounding,
           "greedy": run_greedy, "ga": run_ga}
MILP_CAP = 800          # skip the MILP beyond n*m = 800 (keeps runs bounded)


def evaluate(inst, method, failed=None, seed=0):
    t0 = time.time()
    out = run_rounding(inst, seed=seed) if method == "rounding" \
        else METHODS[method](inst)
    elapsed = time.time() - t0
    if out is None:
        return dict(score=np.nan, makespan=np.nan, feasible=0,
                    runtime_s=elapsed)
    assign, ell = out
    y = inst.forward_pass(assign, ell)
    return dict(score=inst.score(ell, failed=failed),
                makespan=float(y.max()),
                feasible=int(y.max() <= inst.t_max * 1.001),
                runtime_s=elapsed)


def sweep(kind, tasks=50, nodes=5, reps=5, seed=0):
    rows = []
    grid = {
        "slack":   [1.0, 1.2, 1.3, 1.5, 2.0],
        "nodes":   [2, 4, 6, 8, 10],
        "size":    [10, 100, 1000],
        "failure": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
    }[kind]
    for x in grid:
        for rep in range(reps):
            s = seed + 1000 * rep
            kw = dict(seed=s)
            if kind == "slack":
                kw.update(n_tasks=tasks, n_nodes=nodes, alpha=x)
            elif kind == "nodes":
                kw.update(n_tasks=tasks, n_nodes=x)
            elif kind == "size":
                kw.update(n_tasks=x, n_nodes=nodes, density=0.05)
            else:
                kw.update(n_tasks=tasks, n_nodes=nodes)
            inst = generate_instance(**kw)
            failed = None
            if kind == "failure":
                failed = np.random.default_rng(s).random(inst.n) < x
            bound = inst.score(np.ones(inst.n), failed=failed)
            for meth in METHODS:
                if meth == "milp" and inst.n * inst.m > MILP_CAP:
                    rows.append(dict(sweep=kind, param=x, method=meth,
                                     rep=rep, score=np.nan, makespan=np.nan,
                                     feasible=np.nan, runtime_s=np.nan,
                                     bound=bound))
                    continue
                r = evaluate(inst, meth, failed=failed, seed=s + rep)
                rows.append(dict(sweep=kind, param=x, method=meth, rep=rep,
                                 bound=bound, **r))
                print(f"{kind}={x} rep={rep} {meth}: "
                      f"score={r['score']:.3f} feas={r['feasible']} "
                      f"({r['runtime_s']:.1f}s)")
    df = pd.DataFrame(rows)
    os.makedirs(RES_DIR, exist_ok=True)
    out = os.path.join(RES_DIR, f"{kind}.csv")
    df.to_csv(out, index=False)
    print("wrote", out)


def plot():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    style = {"milp": dict(marker="o", ls="-", color="#0d2c54",
                          label="MILP"),
             "rounding": dict(marker="s", ls="--", color="#c0392b",
                              label="Relaxation + rounding"),
             "greedy": dict(marker="^", ls=":", color="#27ae60",
                            label="Greedy"),
             "ga": dict(marker="D", ls="-.", color="#8e44ad",
                        label="Metaheuristic (GA)")}
    xlabel = {"slack": r"slack factor $\alpha$",
              "nodes": "federated fog nodes $N$",
              "size": "workflow size (tasks)",
              "failure": "task failure rate"}
    os.makedirs(FIG_DIR, exist_ok=True)
    for kind in ["slack", "nodes", "size", "failure"]:
        csv = os.path.join(RES_DIR, f"{kind}.csv")
        if not os.path.exists(csv):
            continue
        df = pd.read_csv(csv).dropna(subset=["score"])
        fig, ax = plt.subplots(figsize=(3.5, 2.6), dpi=300)
        if "bound" in df.columns:
            bnd = df.groupby("param")["bound"].mean()
            ax.plot(bnd.index, bnd.values, color="#555555", ls="--", lw=1.0,
                    label="Max-accuracy bound")
        for meth, g in df.groupby("method"):
            mean = g.groupby("param")["score"].mean()
            ax.plot(mean.index, mean.values, **style[meth], lw=1.4, ms=4)
        ax.set_xlabel(xlabel[kind], fontsize=9)
        ax.set_ylabel("average accuracy score", fontsize=9)
        ax.tick_params(labelsize=8)
        ax.legend(fontsize=7, framealpha=0.9)
        fig.tight_layout()
        out = os.path.join(FIG_DIR, f"perf_{kind}_accuracy.png")
        fig.savefig(out, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print("wrote", out)
