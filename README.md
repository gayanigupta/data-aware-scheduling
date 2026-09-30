# Data-Aware Scheduling in Federated Fog Systems

IEEE-conference paper on data-aware scheduling of approximate DAG workflows
across federated fog systems, plus the simulator and data that back the
evaluation.

## Main Document

Set **`ieee-data-aware-scheduling.tex`** as the main document in Overleaf
(standard `IEEEtran` conference class, bibliography `cas-refs.bib`).
`IEEEtran.cls` is included for offline compilation.

`dbdbd-abstract.tex` is the separate 1-page DBDBD 2026 poster abstract
(plain `article` class per the official template).

Before submitting, confirm the author list, affiliations, and emails in the
`\author` block, and replace the repository URL placeholder in the
Reproducibility paragraph once the GitHub repo exists.

## Project Structure

| Location | Purpose |
|---|---|
| `ieee-data-aware-scheduling.tex` | Main IEEE conference paper. |
| `dbdbd-abstract.tex` | 1-page DBDBD 2026 abstract submission. |
| `cas-refs.bib` | Bibliography shared by both documents. |
| `IEEEtran.cls` | Official IEEE class file (V1.8b, CTAN) for local builds. |
| `Figures/` | All figures used by the paper (`perf_*` results + the two draw.io diagrams and their PNG exports). |
| `code/fogsim.py` | CLI entry point (`gen` / `sweep` / `plot`). |
| `code/fogsim/` | Simulator package: `instance.py` (DAG/federation generation), `milp.py` (MILP + LP relaxation via HiGHS), `rounding.py`, `greedy.py`, `ga.py` (the three scalable schedulers), `experiments.py` (sweeps and figures). |
| `code/make_figures.py` | Regenerates the two architecture/DAG diagrams. |
| `data/instances/` | Generated workflow instances (JSON). |
| `data/results/` | Sweep CSVs and rendered result figures. |
| `Archive/`, `Sources/` | Reference material from earlier drafts; not compiled. |

## Reproducing the Experiments

Requires Python 3 with NumPy, SciPy, and pandas.

```bash
# generate a workflow instance
python3 code/fogsim.py gen --tasks 50 --nodes 5 --seed 0

# run one experiment sweep -> data/results/<kind>.csv
python3 code/fogsim.py sweep slack   --tasks 30 --nodes 4 --reps 5
python3 code/fogsim.py sweep nodes   --tasks 30 --reps 5
python3 code/fogsim.py sweep size    --nodes 4 --reps 2
python3 code/fogsim.py sweep failure --tasks 30 --nodes 4 --reps 5

# render figures from the CSVs -> data/results/figures/
python3 code/fogsim.py plot

# regenerate the conceptual diagrams -> Figures/
python3 code/make_figures.py
```

The MILP is skipped automatically for instances above 800 assignment
variables (`n*m`), matching the paper's claim that it is the benchmark for
moderate sizes.

## Evidence Boundary

All results are simulation-based. The manuscript makes no claims about
measured energy, cost, security, privacy, or deployment performance.
