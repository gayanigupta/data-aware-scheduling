"""Scheduling instances: the DAG, the fog federation, and random
instance generation.
"""

import json

import numpy as np


class Instance:
    """One scheduling instance.

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

    def forward_pass(self, assign, ell, retry=None):
        """Earliest-start completion times y_i for assignment + fractions.

        retry: optional set of task indices that fail once and are
        re-executed on the same node, paying their execution time twice.
        """
        retry = retry if retry is not None else ()
        y = np.zeros(self.n)
        for i in self.order:
            a = int(assign[i])
            start = max((y[j] + self.comm(j, i, int(assign[j]), a)
                         for j in self.preds[i]), default=0.0)
            y[i] = start + self.t[i, a] * ell[i] * (2 if i in retry else 1)
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

    # Random vertex order fixes edge direction, so the graph is acyclic by
    # construction.  Every non-source task gets at least one predecessor so
    # the DAG stays connected.
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

    # Fog nodes run at different speeds; links have different bandwidths.
    speed = rng.uniform(0.5, 2.0, m)
    t = rng.uniform(1.0, 5.0, n)[:, None] / speed[None, :]
    B = rng.uniform(10.0, 100.0, (m, m))
    np.fill_diagonal(B, np.inf)
    A = rng.uniform(0.8, 2.0, n)
    P = (rng.random((n, m)) > link_drop).astype(int)
    for i in range(n):
        if not P[i].any():
            P[i, rng.integers(m)] = 1

    # Deadline = alpha * optimistic critical path (fastest eligible node per
    # task, zero communication), so alpha = 1 is genuinely tight.
    inst = Instance(t, A, D, B, P, t_max=1.0)
    cp = np.zeros(n)
    for i in inst.order:
        base = float(np.min(t[i][P[i] == 1]))
        cp[i] = base + max((cp[j] for j in inst.preds[i]), default=0.0)
    inst.t_max = alpha * float(cp.max())
    return inst


def save_instance(inst, path):
    """Serialize sparsely: D is stored as an edge list [[j, i, D_ji]],
    so files stay small even for large DAGs."""
    with open(path, "w") as fh:
        json.dump({
            "t": inst.t.tolist(), "A": inst.A.tolist(),
            "edges": [[j, i, float(inst.D[j, i])] for (j, i) in inst.edges],
            "B": np.where(np.isfinite(inst.B), inst.B, 0).tolist(),
            "P": inst.P.tolist(), "t_max": inst.t_max}, fh)


def load_instance(path):
    with open(path) as fh:
        d = json.load(fh)
    t = np.array(d["t"])
    B = np.array(d["B"])
    np.fill_diagonal(B, np.inf)
    n = t.shape[0]
    D = np.zeros((n, n))
    if "edges" in d:                            # sparse format
        for j, i, v in d["edges"]:
            D[j, i] = v
    else:                                       # legacy dense format
        D = np.array(d["D"])
    return Instance(t, np.array(d["A"]), D,
                    B, np.array(d["P"]), float(d["t_max"]))
