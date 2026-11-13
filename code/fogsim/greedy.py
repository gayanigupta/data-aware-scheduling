"""Bandwidth/data-aware greedy scheduler (Algorithm 1 of the paper).

Walks the DAG in dependency order, commits each task to the node that
finishes it earliest, and shrinks a global execution fraction until the
schedule meets the deadline.
"""

import numpy as np


def run_greedy(inst, beta=0.5, delta=0.005, data_aware=True,
               ell_min=0.0):
    # data_aware=False gives the compute-centric baseline: the scheduler
    # assumes transfers are free when picking nodes, but evaluation still
    # charges the real communication delay (Eq. comm)
    # ell_min is the fraction floor: if the deadline is still missed there
    # the run is reported infeasible, so the loop has at most ceil(1/delta)
    # passes even when communication alone exceeds t_max
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
    # tie-break: accuracy density = A_i / mean execution time over eligible
    # nodes, so equal-priority tasks prefer the cheap high-value ones
    denom = np.array([np.mean(inst.t[i][inst.P[i] == 1])
                      for i in range(n)])
    density = inst.A / denom

    # successors and in-degrees drive the ready set; at each step we take
    # the ready task with the highest priority pi (Algorithm 1)
    succ = [[] for _ in range(n)]
    for (j, i) in inst.edges:
        succ[j].append(i)
    indeg0 = [len(inst.preds[i]) for i in range(n)]

    ell = 1.0
    while ell >= ell_min:
        assign = np.full(n, -1)
        y = np.full(n, np.inf)
        indeg = indeg0.copy()
        ready = [i for i in range(n) if indeg[i] == 0]
        while ready:
            i = max(ready, key=lambda k: (priority[k], density[k]))
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
    return None    # even fraction-0 work misses the deadline: infeasible


def _schedule(inst, ell_vec, priority, density, succ, indeg0):
    """One pass of the greedy list scheduler with per-task fractions."""
    n, m = inst.n, inst.m
    assign = np.full(n, -1)
    y = np.full(n, np.inf)
    indeg = list(indeg0)
    ready = [i for i in range(n) if indeg[i] == 0]
    while ready:
        i = max(ready, key=lambda k: (priority[k], density[k]))
        ready.remove(i)
        best, ba = np.inf, -1
        for a in range(m):
            if not inst.P[i, a]:
                continue
            start = max((y[j] + inst.comm(j, i, int(assign[j]), a)
                         for j in inst.preds[i]), default=0.0)
            yi = start + inst.t[i, a] * ell_vec[i]
            if yi < best:
                best, ba = yi, a
        if ba < 0:
            return None, None                   # no eligible node
        assign[i] = ba
        y[i] = best
        for v in succ[i]:
            indeg[v] -= 1
            if indeg[v] == 0:
                ready.append(v)
    return assign, y


def _binding_path(inst, assign, y):
    """Backtrace the predecessor chain that sets the makespan."""
    path = []
    i = int(np.argmax(y))
    while i >= 0:
        path.append(i)
        preds = inst.preds[i]
        if not preds:
            break
        i = max(preds, key=lambda j: y[j]
                + inst.comm(j, path[-1], int(assign[j]), int(assign[i])))
    return path


def run_greedy_cp(inst, beta=0.5, delta=0.005, ell_min=0.0):
    """Greedy variant that shrinks the fraction only on the longest path.

    Same placement policy as run_greedy, but instead of one global
    fraction it repeatedly schedules, finds the path that sets the
    makespan, and lowers ell only on those tasks.  Tasks off the binding
    path keep full accuracy.
    """
    n = inst.n
    mean_bw = float(np.mean(inst.B[np.isfinite(inst.B)]))
    cp = np.zeros(n)
    for i in reversed(inst.order):
        base = float(np.min(inst.t[i][inst.P[i] == 1]))
        nxt = max((cp[j] + inst.D[i, j] / mean_bw for j in range(n)
                   if inst.D[i, j] > 0), default=0.0)
        cp[i] = base + nxt
    priority = beta * inst.A + (1 - beta) * cp
    denom = np.array([np.mean(inst.t[i][inst.P[i] == 1])
                      for i in range(n)])
    density = inst.A / denom
    succ = [[] for _ in range(n)]
    for (j, i) in inst.edges:
        succ[j].append(i)
    indeg0 = [len(inst.preds[i]) for i in range(n)]

    ell = np.ones(n)
    for _ in range(n * int(np.ceil(1 / delta)) + 1):
        assign, y = _schedule(inst, ell, priority, density, succ, indeg0)
        if assign is None:
            return None
        if y.max() <= inst.t_max:
            return assign, ell
        path = _binding_path(inst, assign, y)
        if all(ell[i] <= ell_min for i in path):
            return None            # binding path already at the floor
        for i in path:
            ell[i] = max(ell_min, ell[i] - delta)
    return None
