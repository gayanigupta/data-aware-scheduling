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


def run_blind(inst):
    """Greedy with the bandwidth term switched off -- the compute-centric
    baseline that shows what data-awareness buys on degraded links."""
    return run_greedy(inst, data_aware=False)
from .ga import run_ga

METHODS = {"milp": run_milp, "rounding": run_rounding,
           "greedy": run_greedy, "ga": run_ga}
MILP_CAP = 800          # skip the MILP beyond n*m = 800 (keeps runs bounded)


def evaluate(inst, method, failed=None, seed=0, trials=40):
    t0 = time.time()
    out = run_rounding(inst, trials=trials, seed=seed) \
        if method == "rounding" else \
        (run_blind(inst) if method == "blind" else METHODS[method](inst))
    elapsed = time.time() - t0
    if out is None:
        return dict(score=np.nan, makespan=np.nan, feasible=0,
                    runtime_s=elapsed)
    assign, ell = out
    # retry-once failure model: a failed task occupies its node for twice
    # its execution time but keeps its accuracy when the retry finishes;
    # schedulers then differentiate through deadline feasibility
    y = inst.forward_pass(assign, ell, retry=failed)
    return dict(score=inst.score(ell),
                makespan=float(y.max()),
                feasible=int(y.max() <= inst.t_max * 1.001),
                runtime_s=elapsed)


def sweep(kind, tasks=50, nodes=5, reps=5, seed=0):
    rows = []
    grid = {
        "slack":     [1.0, 1.2, 1.3, 1.5, 2.0],
        "nodes":     [2, 4, 6, 8, 10],
        "size":      [10, 100, 1000],
        "failure":   [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
        "bandwidth": [1.0, 0.5, 0.2, 0.1, 0.05],
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
            if kind == "bandwidth":
                # degrade every inter-node link by the same factor -- the
                # deadline stays where it was committed, modeling links
                # deteriorating during an event
                off = ~np.eye(inst.m, dtype=bool)
                inst.B[off] *= x
            failed = None
            if kind == "failure":
                failed = np.random.default_rng(s).random(inst.n) < x
            bound = inst.score(np.ones(inst.n), failed=failed)
            # randomized rounding re-solves the LP once per trial, so scale
            # the trial count down on large instances (34 s/solve at
            # n*m = 4000) instead of fixing 40 trials for every size
            trials = max(4, min(40, 20000 // (inst.n * inst.m)))
            # the bandwidth sweep adds the bandwidth-blind baseline so the
            # chart can show what data-aware placement is worth
            meths = list(METHODS) + (["blind"] if kind == "bandwidth" else [])
            for meth in meths:
                if meth == "milp" and inst.n * inst.m > MILP_CAP:
                    rows.append(dict(sweep=kind, param=x, method=meth,
                                     rep=rep, score=np.nan, makespan=np.nan,
                                     feasible=np.nan, runtime_s=np.nan,
                                     bound=bound))
                    continue
                r = evaluate(inst, meth, failed=failed, seed=s + rep,
                             trials=trials)
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
                        label="Metaheuristic (GA)"),
             "blind": dict(marker="v", ls=":", color="#7f8c8d",
                           label="Greedy (bandwidth-blind)")}
    xlabel = {"slack": r"slack factor $\alpha$",
              "nodes": "federated fog nodes $N$",
              "size": "workflow size (tasks)",
              "failure": "task failure rate",
              "bandwidth": "link bandwidth scale"}
    os.makedirs(FIG_DIR, exist_ok=True)
    for kind in ["slack", "nodes", "size", "failure", "bandwidth"]:
        csv = os.path.join(RES_DIR, f"{kind}.csv")
        if not os.path.exists(csv):
            continue
        df = pd.read_csv(csv)
        # bandwidth and failure are special: score alone is misleading
        # (the blind baseline / retried tasks report full accuracy while
        # missing the deadline) -- so these get a feasibility panel too
        two_panel = kind in ("bandwidth", "failure")
        fig, axs = plt.subplots(1, 2 if two_panel else 1,
                                figsize=(6.6 if two_panel else 3.5,
                                         2.6), dpi=300)
        ax = axs[0] if two_panel else axs
        df_s = df.dropna(subset=["score"])
        if "bound" in df_s.columns:
            bnd = df_s.groupby("param")["bound"].mean()
            ax.plot(bnd.index, bnd.values, color="#555555", ls="--", lw=1.0,
                    label="Max-accuracy bound")
        for meth, g in df_s.groupby("method"):
            mean = g.groupby("param")["score"].mean()
            ax.plot(mean.index, mean.values, **style[meth], lw=1.4, ms=4)
        ax.set_xlabel(xlabel[kind], fontsize=9)
        ax.set_ylabel("average accuracy score", fontsize=9)
        ax.tick_params(labelsize=8)
        ax.legend(fontsize=7, framealpha=0.9)
        if two_panel:
            ax2 = axs[1]
            for meth, g in df.groupby("method"):
                feas = g.groupby("param")["feasible"].mean()
                ax2.plot(feas.index, feas.values, **style[meth], lw=1.4, ms=4)
            ax2.set_xlabel(xlabel[kind], fontsize=9)
            ax2.set_ylabel("deadline feasibility rate", fontsize=9)
            ax2.set_ylim(-0.05, 1.05)
            ax2.tick_params(labelsize=8)
        fig.tight_layout()
        out = os.path.join(FIG_DIR, f"perf_{kind}_accuracy.png")
        fig.savefig(out, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print("wrote", out)
