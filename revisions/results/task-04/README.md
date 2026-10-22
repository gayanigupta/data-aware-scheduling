# Task 4 — What happens when a task runs at 0%

**Chosen fix:** option (b) — document the semantics of a skipped task.
Option (a) (a minimum fraction l >= 0.1) was not needed: the measurement
below shows skipped tasks never appear in certified-optimal solutions,
so changing the model would add a constraint for a case that does not
occur and would force a full rerun of every experiment.

## What a skipped task sends

A task with ell_i = 0 performs no work and earns no accuracy, but the
data D_ji on its outgoing edges is still delivered to its successors —
the payload is a workflow input, not a function of the fraction run.
So the transfer cost is charged whether or not the task ran. This is
what the code has always done (`Instance.comm()` ignores ell), and the
paper now says it in words after constraint (7).

## Evidence

`skipped_tasks.csv` — every MILP run re-solved, fraction vector decoded:

- 117 runs solved, 7 skipped over the model-size cap.
- 40 skipped tasks out of 5,910 total (0.68%).
- All 40 sit in the 13 runs that hit the time limit (alpha=1.0 or
  bandwidth scale <= 0.2) — unpolished incumbents.
- Every run that certified optimality has zero skipped tasks.

Conclusion: skipping is a corner the incumbent may pass through under a
time limit, not a property of optimal schedules. Documenting the
semantics is sufficient.

## Files

- `check_skipped_tasks.py` — regenerates `skipped_tasks.csv`
- `skipped_tasks.csv` — per-run skipped-task counts
- `MILP_skipped_tasks.docx` — the write-up
- `paper/main.tex` — sentence after constraint (7)
- `code/fogsim/instance.py` — `comm()` documents the same semantics
