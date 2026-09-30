"""Randomized rounding of the LP relaxation (Section V-A of the paper).

The relaxed assignment values act as a sampling distribution; each rounded
placement is then scored after a second LP solve fixes the assignment and
re-optimizes the execution fractions.
"""

import numpy as np

from .milp import solve_relaxed


def run_rounding(inst, trials=40, seed=0):
    rng = np.random.default_rng(seed)
    res = solve_relaxed(inst)
    if not res.success:
        return None
    n, m, nm = inst.n, inst.m, inst.n * inst.m
    frac = res.x[:nm].reshape(n, m)

    best, best_score = None, -np.inf
    for _ in range(trials):
        e = np.zeros((n, m))
        assign = np.zeros(n, dtype=int)
        for i in range(n):
            p = np.where(inst.P[i] == 1, np.maximum(frac[i], 0.0), 0.0)
            if p.sum() <= 0:                       # degenerate: take any eligible
                a = int(np.random.default_rng(seed + i)
                        .choice(np.nonzero(inst.P[i])[0]))
            else:
                a = int(rng.choice(m, p=p / p.sum()))
            assign[i] = a
            e[i, a] = 1.0
        refit = solve_relaxed(inst, fix_e=e)
        if not refit.success:
            continue
        l = refit.x[nm:2 * nm].reshape(n, m)
        ell = np.clip([l[i, a] for i, a in enumerate(assign)], 0, 1)
        y = inst.forward_pass(assign, ell)
        if y.max() > inst.t_max * 1.001:
            continue
        s = inst.score(ell)
        if s > best_score:
            best, best_score = (assign, ell), s
    return best
