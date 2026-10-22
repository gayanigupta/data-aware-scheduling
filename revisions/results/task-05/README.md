# Task 5 — Approximation assumptions paragraph

**Changed in:** `paper/main.tex`, Section III, "Assumptions" subsection.

A short paragraph (~130 words, under the 150-word limit) now follows the
assumption list and explains:

- what running 50% of a task means (half of a full-quality result);
- a real example (an iterative solver stopped after half its iterations;
  also every-other-frame video processing and early-stopped training);
- why time and accuracy are assumed linear (same work executed fewer
  times; incremental algorithms gain quality roughly with effort);
- the limits (all-or-nothing tasks, saturating accuracy curves, ignored
  fixed startup cost) and why we keep it (makes the deadline-accuracy
  trade-off explicit and keeps the formulation linear).
