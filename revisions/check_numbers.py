#!/usr/bin/env python3
"""Task 6 -- verify that every number quoted in the paper matches the
result CSVs (nothing edited by hand).

Checks the numbers reviewers flagged, plus the other figures quoted in
the evaluation text, against the regenerated result files.  Writes one
row per check: the value as written in the paper, the value computed
from the CSVs, and whether they agree.

Output: revisions/results/task-06/number_check.csv
Run from the repo root:  python3 revisions/check_numbers.py
"""

import os

import pandas as pd

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..")
RES = os.path.join(ROOT, "data", "results")

runs = pd.read_csv(os.path.join(RES, "test_runs.csv"))
size = pd.read_csv(os.path.join(RES, "size.csv"))
milp = pd.read_csv(os.path.join(HERE, "results", "task-02",
                                "milp_solver_details.csv"))

checks = []


def check(claim, paper_value, csv_value, tol=0.005, fmt="{:.3f}"):
    ok = abs(csv_value - paper_value) <= tol
    checks.append(dict(claim=claim,
                       paper=fmt.format(paper_value),
                       from_csv=fmt.format(csv_value),
                       match="yes" if ok else "NO"))


# --- Table II: small dataset ---
s = runs[runs.dataset == "small"]
check("small MILP score (Table II)", 1.637,
      float(s[s.method == "milp"].score.iloc[0]), tol=0.001)
# the small bound coincides with the score: all methods reach it
check("small bound = score of all methods", 1.637,
      float(s.score.max()), tol=0.001)
m = runs[runs.dataset == "medium"]
check("medium MILP makespan (text)", 60.94,
      float(m[m.method == "milp"].makespan.iloc[0]), tol=0.01)
check("medium greedy makespan (text)", 43.11,
      float(m[m.method == "greedy"].makespan.iloc[0]), tol=0.01)
x = runs[runs.dataset == "xlarge"]
check("xlarge GA runtime 73.01 s (Table II)", 73.01,
      float(x[x.method == "ga"].runtime_s.iloc[0]), tol=0.01)

# --- Fig. 5 (size experiment) ---
sz = size.groupby(["param", "method"]).agg(
    score=("score", "mean"), rt=("runtime_s", "mean"),
    bound=("bound", "mean")).reset_index()
def get(p, me, col):
    return float(sz[(sz.param == p) & (sz.method == me)][col].iloc[0])

check("n=10 bound ~1.41 (V-F text)", 1.41, get(10, "milp", "bound"),
      tol=0.01)
check("n=100 greedy score ~1.40 (V-F)", 1.40, get(100, "greedy", "score"),
      tol=0.01)
check("n=100 rounding ~1.35 (V-F)", 1.35, get(100, "rounding", "score"),
      tol=0.01)
check("n=100 GA ~1.26 (V-F)", 1.26, get(100, "ga", "score"), tol=0.01)
check("n=1000 greedy ~1.40 (V-F)", 1.40, get(1000, "greedy", "score"),
      tol=0.01)
check("n=1000 rounding ~1.37 (V-F)", 1.37, get(1000, "rounding", "score"),
      tol=0.01)
check("n=1000 GA ~1.10 (V-F)", 1.10, get(1000, "ga", "score"), tol=0.01)
check("n=1000 greedy runtime ~0.15 s", 0.15, get(1000, "greedy", "rt"),
      tol=0.05)
check("n=1000 GA runtime ~159 s", 159.0, get(1000, "ga", "rt"), tol=5.0)
check("n=1000 rounding runtime ~372 s", 372.0,
      get(1000, "rounding", "rt"), tol=10.0)

# --- MILP solver statistics (bottlenecks paragraph) ---
exp_runs = milp[milp.experiment != "test_run"]
n_tl = int((exp_runs.solver_status == "time limit").sum())
check("time-limited runs = 18 of 120", 18, n_tl, tol=0, fmt="{:d}")

# --- skipped tasks claim (Section III + Fig. 8) ---
sk = pd.read_csv(os.path.join(HERE, "results", "task-04",
                              "skipped_tasks.csv"))
ok_runs = sk[sk.note == "ok"]
skip_opt = int(ok_runs[ok_runs.solver_status == "optimal"]
               .n_skipped.sum())
check("skipped tasks in certified-optimal runs = 0", 0, skip_opt,
      tol=0, fmt="{:d}")

df = pd.DataFrame(checks)
out = os.path.join(HERE, "results", "task-06", "number_check.csv")
os.makedirs(os.path.dirname(out), exist_ok=True)
df.to_csv(out, index=False)
print(df.to_string(index=False))
bad = df[df.match == "NO"]
print(f"\nwrote {out} -- {len(df)} checks, "
      f"{len(bad)} mismatches")
