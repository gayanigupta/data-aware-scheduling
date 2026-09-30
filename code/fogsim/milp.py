"""The MILP of Section IV of the paper, solved with the HiGHS solver
through scipy.optimize.milp, plus the LP relaxation used by the
randomized-rounding scheduler.
"""

import numpy as np
from scipy.optimize import milp, linprog, LinearConstraint, Bounds
from scipy.sparse import lil_matrix, vstack as sp_vstack


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


def solve_relaxed(inst, fix_e=None):
    """Solve the LP relaxation, optionally with the assignment fixed."""
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
