# Task 3 — Lemma 4 and Theorem 1 wording

**Changed in:** `paper/main.tex`, appendix "Correctness and Linearization".

## Lemma (`lem:timing`, "Lemma 4")

Before: "The minimal possible M_ia is the earliest time T_i can start on
f_a" — but nothing in the model forces start times to be minimal.

After: the lemma now states the property the model actually enforces —
in any feasible solution, M_ia respects data arrival (no task starts
before every predecessor completes and its output reaches f_a). The
proof keeps the induction and notes that earliest-start is recovered by
setting M_ia to the bound, while larger deadline-feasible values are
equally valid. `lem:completion` and `lem:deadline` were reworded to
drop the "earliest" dependence accordingly.

## Theorem (`thm:correspondence`, "Theorem 1")

Before: "Any optimal solution is feasible and maximizes the total
achieved accuracy" — the proof just restated the objective.

After: the theorem states a two-way correspondence — feasible solutions
are exactly the valid schedules, and the objective counts exactly the
schedule's achieved accuracy — so the MILP optimum equals the best
achievable accuracy. The proof now argues both directions, including
constructing a feasible solution from any valid schedule.

Verification: `main.pdf` recompiles cleanly; labels/numbering unchanged.
