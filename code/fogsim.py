#!/usr/bin/env python3
"""fogsim -- simulator for data-/bandwidth-aware DAG scheduling in
federated fog systems, matching the model and algorithms of the paper.

Implements the four schedulers:
  * milp      -- exact MILP via scipy.optimize.milp (HiGHS backend)
  * rounding  -- LP relaxation + randomized rounding of the assignment
  * greedy    -- Algorithm 1: bandwidth/data-aware greedy DAG scheduler
  * ga        -- Algorithm 2: genetic algorithm

Subcommands (run from the project root):
  gen    generate a JSON instance -> data/instances/
  sweep  run one of {slack,nodes,size,failure} -> data/results/*.csv
  plot   render sweep CSVs -> data/results/figures/*.png

Examples:
  python3 code/fogsim.py gen --tasks 50 --nodes 5 --seed 0
  python3 code/fogsim.py sweep slack --tasks 30 --nodes 4 --reps 3
  python3 code/fogsim.py plot
"""

from __future__ import annotations

import argparse
import json
import os
import time

import numpy as np
import pandas as pd
from scipy.optimize import milp, linprog, LinearConstraint, Bounds
from scipy.sparse import lil_matrix, vstack as sp_vstack

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
INST_DIR = os.path.join(ROOT, "data", "instances")
RES_DIR = os.path.join(ROOT, "data", "results")
FIG_DIR = os.path.join(RES_DIR, "figures")


# ---------------------------------------------------------------- model

class Instance:
    """Scheduling instance.

    t[n,m]   full execution time of task i on node a
    A[n]     accuracy weight of task i (the score is sum_i A_i*ell_i / n,
             so it is NOT bounded by 1 -- see the paper's metrics paragraph)
    D[n,n]   data size of edge (j,i); 0 if the edge does not exist
    B[m,m]   bandwidth of link (b,a); diagonal = inf
    P[n,m]   eligibility {0,1}
    """

    def __init__(self, t, A, D, B, P, t_max):
        self.t, self.A, self.D = t, A, D
        self.B, self.P = B, P
        self.t_max = t_max
        self.n, self.m = t.shape
        self.preds = [list(np.nonzero(D[:, i])[0]) for i in range(self.n)]
        self.edges = [(int(j), int(i)) for i in range(self.n)
                      for j in self.preds[i]]
        self.order = self._topo()

    def _topo(self):
        succ = [[] for _ in range(self.n)]
        deg = [len(p) for p in self.preds]
        for (j, i) in self.edges:
            succ[j].append(i)
        order, stack = [], [i for i in range(self.n) if deg[i] == 0]
        while stack:
            u = stack.pop()
            order.append(u)
            for v in succ[u]:
                deg[v] -= 1
                if deg[v] == 0:
                    stack.append(v)
        return order

    def comm(self, j, i, b, a):
        """Communication delay c_{ji}^{ba} (Eq. comm of the paper)."""
        return 0.0 if b == a else self.D[j, i] / self.B[b, a]

    def forward_pass(self, assign, ell):
        """Earliest-start completion times y_i for assignment + fractions."""
        y = np.zeros(self.n)
        for i in self.order:
            a = int(assign[i])
            start = max((y[j] + self.comm(j, i, int(assign[j]), a)
                         for j in self.preds[i]), default=0.0)
            y[i] = start + self.t[i, a] * ell[i]
        return y

    def score(self, ell, failed=None):
        e = np.asarray(ell, float).copy()
        if failed is not None:
            e[failed] = 0.0
        return float(np.mean(self.A * e))


def generate_instance(n_tasks=50, n_nodes=5, density=0.15, alpha=1.5,
                      seed=0, link_drop=0.15):
    """Reproducible random instance: DAG + heterogeneous fog federation."""
    rng = np.random.default_rng(seed)
    n, m = n_tasks, n_nodes

    # DAG: random vertex order fixes direction; every non-source keeps >=1 pred
    perm = rng.permutation(n)
    pos = np.empty(n, int)
    pos[perm] = np.arange(n)
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if pos[j] < pos[i] and rng.random() < density:
                D[j, i] = rng.uniform(5.0, 50.0)
    for i in range(n):
        if pos[i] > 0 and not np.any(D[:, i]):
            j = perm[rng.integers(0, pos[i])]
            D[j, i] = rng.uniform(5.0, 50.0)

    speed = rng.uniform(0.5, 2.0, m)
    t = rng.uniform(1.0, 5.0, n)[:, None] / speed[None, :]
    B = rng.uniform(10.0, 100.0, (m, m))
    np.fill_diagonal(B, np.inf)
    A = rng.uniform(0.8, 2.0, n)
    P = (rng.random((n, m)) > link_drop).astype(int)
    for i in range(n):
        if not P[i].any():
            P[i, rng.integers(m)] = 1

    # critical path at full execution with fastest eligible node and the
    # optimistic (zero-communication) bound, so alpha=1 is genuinely tight
    inst = Instance(t, A, D, B, P, t_max=1.0)
    cp = np.zeros(n)
    for i in inst.order:
        base = float(np.min(t[i][P[i] == 1]))
        cp[i] = base + max((cp[j] for j in inst.preds[i]), default=0.0)
    inst.t_max = alpha * float(cp.max())
    return inst


def save_instance(inst, path):
    json.dump({
        "t": inst.t.tolist(), "A": inst.A.tolist(), "D": inst.D.tolist(),
        "B": np.where(np.isfinite(inst.B), inst.B, 0).tolist(),
        "P": inst.P.tolist(), "t_max": inst.t_max}, open(path, "w"))


def load_instance(path):
    d = json.load(open(path))
    B = np.array(d["B"])
    np.fill_diagonal(B, np.inf)
    return Instance(np.array(d["t"]), np.array(d["A"]), np.array(d["D"]),
                    B, np.array(d["P"]), float(d["t_max"]))


# ------------------------------------------------- MILP / LP formulation

def _build_lp(inst):
    """Linear constraints shared by the MILP and its LP relaxation.

    Variables: e[n*m] (assignment), l[n*m] (execution fraction), y[n].
    The start-time constraint of Eq.(start) is written in big-M form:
      y_j - y_i + sum_b e_jb c_ji^{ba} + t_ia l_ia + M e_ia <= M
    which is y_i >= y_j + comm + exec exactly when e_ia = 1, and is
    vacuous otherwise (M = t_max + max communication delay).
    """
    n, m = inst.n, inst.m
    nm = n * m
    nv = 2 * nm + n

    def ei(i, a): return i * m + a
    def li(i, a): return nm + i * m + a
    def yi(i):    return 2 * nm + i

    M = inst.t_max + float(np.max(
        [inst.D[j, i] / inst.B[b, a]
         for (j, i) in inst.edges for b in range(m) for a in range(m)
         if b != a], initial=0.0)) + 1.0

    rows, lo, hi = [], [], []

    def add(coefs, lb=-np.inf, ub=np.inf):
        rows.append(coefs); lo.append(lb); hi.append(ub)

    for i in range(n):                                   # sum_a e_ia = 1
        add({ei(i, a): 1.0 for a in range(m)}, 1.0, 1.0)
    for i in range(n):                                   # l_ia <= e_ia
        for a in range(m):
            add({li(i, a): 1.0, ei(i, a): -1.0}, ub=0.0)
    for i in range(n):                                   # start times
        for a in range(m):
            base = {yi(i): -1.0, li(i, a): inst.t[i, a], ei(i, a): M}
            if not inst.preds[i]:
                add(base, ub=M)
            else:
                for j in inst.preds[i]:
                    r = dict(base)
                    r[yi(j)] = r.get(yi(j), 0.0) + 1.0
                    for b in range(m):
                        r[ei(j, b)] = r.get(ei(j, b), 0.0) \
                            + inst.comm(j, i, b, a)
                    add(r, ub=M)

    A = lil_matrix((len(rows), nv))
    for k, coefs in enumerate(rows):
        for col, v in coefs.items():
            A[k, col] = v
    con = LinearConstraint(A.tocsr(), np.array(lo), np.array(hi))

    c = np.zeros(nv)
    for i in range(n):
        for a in range(m):
            c[li(i, a)] = -inst.A[i] / n                 # maximize accuracy

    lb = np.zeros(nv)
    ub = np.empty(nv)
    for i in range(n):
        for a in range(m):
            ub[ei(i, a)] = inst.P[i, a]                  # e_ia <= P_ia
            ub[li(i, a)] = 1.0
        ub[yi(i)] = inst.t_max                           # y_i <= t_max
    return c, con, Bounds(lb, ub), nv, nm


def _extract(res, inst):
    """Recover assignment and per-task fraction from a solver result."""
    n, m, nm = inst.n, inst.m, inst.n * inst.m
    e = res.x[:nm].reshape(n, m)
    l = res.x[nm:2 * nm].reshape(n, m)
    assign = np.argmax(np.where(inst.P == 1, np.round(e), -np.inf), axis=1)
    ell = np.array([l[i, assign[i]] for i in range(n)])
    ell = np.clip(np.nan_to_num(ell), 0.0, 1.0)
    return assign, ell


def run_milp(inst, time_limit=60.0):
    c, con, bounds, nv, _ = _build_lp(inst)
    integ = np.zeros(nv)
    integ[:inst.n * inst.m] = 1.0
    res = milp(c, constraints=con, integrality=integ, bounds=bounds,
               options={"time_limit": time_limit, "mip_rel_gap": 1e-4})
    if res.x is None:
        return None
    return _extract(res, inst)


def _solve_relaxed(inst, fix_e=None):
    c, con, bounds, nv, nm = _build_lp(inst)
    lb, ub = bounds.lb.copy(), bounds.ub.copy()
    if fix_e is not None:
        lb[:nm] = ub[:nm] = fix_e.reshape(-1)

    # linprog takes A_ub x <= b_ub and A_eq x == b_eq; split the
    # LinearConstraint into its equality and inequality parts.
    A = con.A
    lo, hi = con.lb, con.ub
    eq_mask = (lo == hi)
    ub_mask = ~eq_mask & np.isfinite(hi)
    lb_mask = ~eq_mask & np.isfinite(lo)
    A_ub = sp_vstack([A[ub_mask], -A[lb_mask]]).tocsr()
    b_ub = np.concatenate([hi[ub_mask], -lo[lb_mask]])
    A_eq = A[eq_mask].tocsr()
    b_eq = hi[eq_mask]
    return linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                   bounds=list(zip(lb, ub)), method="highs")


def run_rounding(inst, trials=40, seed=0):
    rng = np.random.default_rng(seed)
    res = _solve_relaxed(inst)
    if not res.success:
        return None
    n, m, nm = inst.n, inst.m, inst.n * inst.m
    r = res.x[:nm].reshape(n, m)

    best, best_score = None, -np.inf
    for _ in range(trials):
        e = np.zeros((n, m))
        assign = np.zeros(n, dtype=int)
        for i in range(n):
            p = np.where(inst.P[i] == 1, np.maximum(r[i], 0.0), 0.0)
            if p.sum() <= 0:                       # degenerate: take best P
                a = int(np.random.default_rng(seed + i)
                        .choice(np.nonzero(inst.P[i])[0]))
            else:
                a = int(rng.choice(m, p=p / p.sum()))
            assign[i] = a
            e[i, a] = 1.0
        r2 = _solve_relaxed(inst, fix_e=e)
        if not r2.success:
            continue
        l = r2.x[nm:2 * nm].reshape(n, m)
        ell = np.clip([l[i, a] for i, a in enumerate(assign)], 0, 1)
        y = inst.forward_pass(assign, ell)
        if y.max() > inst.t_max * 1.001:
            continue
        s = inst.score(ell)
        if s > best_score:
            best, best_score = (assign, ell), s
    return best


# ---------------------------------------------------------------- greedy

def run_greedy(inst, beta=0.5, delta=0.005):
    """Algorithm 1: global execution fraction + earliest-finish placement."""
    n, m = inst.n, inst.m
    Bm = float(np.mean(inst.B[np.isfinite(inst.B)]))

    # CP_i: critical-path length from task i to a sink (urgency term, Eq. priority)
    cp = np.zeros(n)
    for i in reversed(inst.order):
        base = float(np.min(inst.t[i][inst.P[i] == 1]))
        nxt = max((cp[j] + inst.D[i, j] / Bm for j in range(n)
                   if inst.D[i, j] > 0), default=0.0)
        cp[i] = base + nxt

    pi = beta * inst.A + (1 - beta) * cp

    ell = 1.0
    while ell > 0:
        assign = np.full(n, -1)
        y = np.full(n, np.inf)
        done = np.zeros(n, bool)
        for i in inst.order:                       # dependency order == ready
            best, ba = np.inf, -1
            for a in range(m):
                if not inst.P[i, a]:
                    continue
                start = max((y[j] + inst.comm(j, i, int(assign[j]), a)
                             for j in inst.preds[i]), default=0.0)
                yi = start + inst.t[i, a] * ell
                if yi < best:
                    best, ba = yi, a
            if ba < 0:
                return None                        # no eligible node
            assign[i] = ba
            y[i] = best
            done[i] = True
        if y.max() <= inst.t_max:
            return assign, np.full(n, ell)
        ell -= delta
    return assign, np.full(n, max(ell, 0.0))       # best effort below deadline


# -------------------------------------------------------------------- GA

def run_ga(inst, pop_size=40, gens=60, seed=0,
           lam1=10.0, lam2=1.0, sigma=0.1):
    """Algorithm 2: chromosome = (assignment f, fractions ell)."""
    rng = np.random.default_rng(seed)
    n, m = inst.n, inst.m
    elig = [list(np.nonzero(inst.P[i])[0]) for i in range(n)]

    def fitness(ind):
        f, ell = ind
        y = inst.forward_pass(f, ell)
        viol = max(0.0, y.max() - inst.t_max)
        return (np.mean(inst.A * ell)
                - lam1 * float(viol > 0)
                - lam2 * viol / inst.t_max)

    def make():
        f = np.array([rng.choice(e) for e in elig])
        # seeding: co-locate with the heaviest predecessor when eligible
        for i in range(n):
            if inst.preds[i] and rng.random() < 0.5:
                j = max(inst.preds[i], key=lambda j: inst.D[j, i])
                if f[j] in elig[i]:
                    f[i] = f[j]
        return f, rng.uniform(0.5, 1.0, n)

    pop = [make() for _ in range(pop_size)]
    for _ in range(gens):
        fits = np.array([fitness(ind) for ind in pop])
        top = np.argsort(fits)[-2:]                # elitism k=2
        children = [pop[i] for i in top]
        while len(children) < pop_size:
            p1, p2 = (pop[max(rng.integers(pop_size, size=3),
                             key=lambda k: fitness(pop[k]))]
                      for _ in range(2))
            cut = rng.integers(1, n)
            f = np.concatenate([p1[0][:cut], p2[0][cut:]])
            ell = np.concatenate([p1[1][:cut], p2[1][cut:]])
            mut = rng.random(n) < 0.1
            for i in np.nonzero(mut)[0]:
                f[i] = rng.choice(elig[i])
                ell[i] = np.clip(ell[i] + rng.normal(0, sigma), 0, 1)
            if inst.preds[i := int(rng.integers(n))]:
                j = max(inst.preds[i], key=lambda j: inst.D[j, i])
                if f[j] in elig[i]:
                    f[i] = f[j]                   # repair: co-locate big edge
            children.append((f, ell))
        pop = children
    best = max(pop, key=fitness)
    y = inst.forward_pass(best[0], best[1])
    return best


# ------------------------------------------------------------- sweeps

METHODS = {"milp": run_milp, "rounding": run_rounding,
           "greedy": run_greedy, "ga": run_ga}
MILP_CAP = 800          # skip the MILP beyond n*m = 800 (keeps runs bounded)


def evaluate(inst, method, failed=None, seed=0):
    t0 = time.time()
    out = METHODS[method](inst) if method != "rounding" \
        else METHODS[method](inst, seed=seed)
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


# -------------------------------------------------------------------- CLI

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gen", help="generate an instance JSON")
    g.add_argument("--tasks", type=int, default=50)
    g.add_argument("--nodes", type=int, default=5)
    g.add_argument("--alpha", type=float, default=1.5)
    g.add_argument("--seed", type=int, default=0)
    g.add_argument("--out", default=None)

    s = sub.add_parser("sweep", help="run an experiment sweep -> CSV")
    s.add_argument("kind", choices=["slack", "nodes", "size", "failure"])
    s.add_argument("--tasks", type=int, default=50)
    s.add_argument("--nodes", type=int, default=5)
    s.add_argument("--reps", type=int, default=5)
    s.add_argument("--seed", type=int, default=0)

    sub.add_parser("plot", help="render sweep CSVs to PNG figures")

    args = ap.parse_args()

    if args.cmd == "gen":
        inst = generate_instance(n_tasks=args.tasks, n_nodes=args.nodes,
                                 alpha=args.alpha, seed=args.seed)
        os.makedirs(INST_DIR, exist_ok=True)
        out = args.out or os.path.join(
            INST_DIR, f"dag{args.tasks}_nodes{args.nodes}"
                      f"_a{args.alpha}_s{args.seed}.json")
        save_instance(inst, out)
        print("wrote", out)
    elif args.cmd == "sweep":
        sweep(args.kind, tasks=args.tasks, nodes=args.nodes,
              reps=args.reps, seed=args.seed)
    else:
        plot()


if __name__ == "__main__":
    main()
