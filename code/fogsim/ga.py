"""Genetic-algorithm scheduler (Algorithm 2 of the paper).

A chromosome is a full placement vector plus a per-task execution
fraction; fitness is the achieved accuracy minus deadline-violation
penalties.
"""

import numpy as np


def run_ga(inst, pop_size=40, gens=60, seed=0,
           lam1=10.0, lam2=1.0, sigma=0.1):
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
            # tournament of 3 per parent, one-point crossover on both
            # the assignment and the fraction vectors
            p1, p2 = (pop[max(rng.integers(pop_size, size=3),
                             key=lambda k: fitness(pop[k]))]
                      for _ in range(2))
            cut = rng.integers(1, n)
            f = np.concatenate([p1[0][:cut], p2[0][cut:]])
            ell = np.concatenate([p1[1][:cut], p2[1][cut:]])

            mutate = rng.random(n) < 0.1
            for i in np.nonzero(mutate)[0]:
                f[i] = rng.choice(elig[i])
                ell[i] = np.clip(ell[i] + rng.normal(0, sigma), 0, 1)

            # repair: co-locate one random task with the predecessor that
            # sends it the most data, when that node is eligible
            i = int(rng.integers(n))
            if inst.preds[i]:
                j = max(inst.preds[i], key=lambda j: inst.D[j, i])
                if f[j] in elig[i]:
                    f[i] = f[j]
            children.append((f, ell))
        pop = children
    return max(pop, key=fitness)
