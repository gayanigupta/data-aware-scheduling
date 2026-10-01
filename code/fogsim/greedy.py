"""Bandwidth/data-aware greedy scheduler (Algorithm 1 of the paper).

Walks the DAG in dependency order, commits each task to the node that
finishes it earliest, and shrinks a global execution fraction until the
schedule meets the deadline.
"""

import numpy as np


def run_greedy(inst, beta=0.5, delta=0.005, data_aware=True):
    # data_aware=False gives the compute-centric baseline: the scheduler
    # assumes transfers are free when picking nodes, but evaluation still
    # charges the real communication delay (Eq. comm)
    n, m = inst.n, inst.m
    mean_bw = float(np.mean(inst.B[np.isfinite(inst.B)]))

    # Critical-path distance to a sink, used as the urgency term in the
    # priority score (Eq. priority of the paper).
    cp = np.zeros(n)
    for i in reversed(inst.order):
        base = float(np.min(inst.t[i][inst.P[i] == 1]))
        nxt = max((cp[j] + inst.D[i, j] / mean_bw for j in range(n)
                   if inst.D[i, j] > 0), default=0.0)
        cp[i] = base + nxt

    priority = beta * inst.A + (1 - beta) * cp

    # successors and in-degrees drive the ready set; at each step we take
    # the ready task with the highest priority pi (Algorithm 1)
    succ = [[] for _ in range(n)]
    for (j, i) in inst.edges:
        succ[j].append(i)
    indeg0 = [len(inst.preds[i]) for i in range(n)]

    ell = 1.0
    while ell > 0:
        assign = np.full(n, -1)
        y = np.full(n, np.inf)
        indeg = indeg0.copy()
        ready = [i for i in range(n) if indeg[i] == 0]
        while ready:
            i = max(ready, key=lambda k: priority[k])
            ready.remove(i)
            best, ba = np.inf, -1
            for a in range(m):
                if not inst.P[i, a]:
                    continue
                start = max((y[j] + (inst.comm(j, i, int(assign[j]), a)
                                     if data_aware else 0.0)
                             for j in inst.preds[i]), default=0.0)
                yi = start + inst.t[i, a] * ell
                if yi < best:
                    best, ba = yi, a
            if ba < 0:
                return None                        # no eligible node
            assign[i] = ba
            y[i] = best
            for v in succ[i]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    ready.append(v)
        if y.max() <= inst.t_max:
            return assign, np.full(n, ell)
        ell -= delta
    return assign, np.full(n, max(ell, 0.0))       # best effort below deadline
