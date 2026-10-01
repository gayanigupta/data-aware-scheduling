# Data-Aware Scheduling in Federated Fog Systems

IEEE-conference paper on data-aware scheduling of approximate DAG workflows
across federated fog systems, plus the simulator and data that back the
evaluation.

## Main Document

Everything needed to compile the paper lives in **`paper/`** — open that
folder in Overleaf (or import the repo) and set **`paper/main.tex`** as the
main document (standard `IEEEtran` conference class; `IEEEtran.cls` and the
bibliography `cas-refs.bib` are included so it also compiles offline).

`paper/dbdbd-abstract.tex` is the separate 1-page DBDBD 2026 poster
abstract (plain `article` class per the official template).

Before submitting, confirm the author list, affiliations, and emails in the
`\author` block of `paper/main.tex`.

## Project Structure

| Location | Purpose |
|---|---|
| `paper/main.tex` | Main IEEE conference paper (Overleaf entry point). |
| `paper/dbdbd-abstract.tex` | 1-page DBDBD 2026 abstract submission. |
| `paper/cas-refs.bib` | Bibliography shared by both documents. |
| `paper/IEEEtran.cls` | Official IEEE class file (V1.8b, CTAN) for local builds. |
| `paper/Figures/` | All figures used by the paper (`perf_*` results + the two draw.io-style diagrams). |
| `code/fogsim.py` | CLI entry point (`gen` / `sweep` / `plot`). |
| `code/fogsim/` | Simulator package: `instance.py` (DAG/federation generation), `milp.py` (MILP + LP relaxation via HiGHS), `rounding.py`, `greedy.py`, `ga.py` (the three scalable schedulers), `experiments.py` (sweeps and figures). |
| `code/make_figures.py` | Regenerates the two architecture/DAG diagrams. |
| `data/instances/` | Generated workflow instances (JSON). |
| `data/results/` | Sweep CSVs and rendered result figures. |
| `Sources/` | Reference material from earlier drafts; not compiled. |

## Reproducing the Experiments

Requires Python 3 with NumPy, SciPy, and pandas.

```bash
# generate a workflow instance
python3 code/fogsim.py gen --tasks 50 --nodes 5 --seed 0

# run one experiment sweep -> data/results/<kind>.csv
python3 code/fogsim.py sweep slack     --tasks 30 --nodes 4 --reps 5
python3 code/fogsim.py sweep nodes     --tasks 30 --reps 5
python3 code/fogsim.py sweep size      --nodes 4 --reps 2
python3 code/fogsim.py sweep failure   --tasks 30 --nodes 4 --reps 5
python3 code/fogsim.py sweep bandwidth --tasks 50 --nodes 5 --reps 3

# render figures from the CSVs -> data/results/figures/
python3 code/fogsim.py plot

# regenerate the conceptual diagrams -> paper/Figures/
python3 code/make_figures.py
```

The MILP is skipped automatically for instances above 800 assignment
variables (`n*m`), matching the paper's claim that it is the benchmark for
moderate sizes.

## Notebook

`notebooks/experiments.ipynb` is an executed notebook that walks through the
datasets, the per-dataset test runs (`data/results/test_runs.csv`), the
workflow/resource graphs (including structural DAGs up to 10^6 tasks and
federations up to 10^6 nodes), all five comparative charts used in the paper,
an asymptotic runtime analysis, and a plain-language account of where the
current implementation hits its scaling limits. Open it in Jupyter and run
all cells to regenerate every artifact.

## Evidence Boundary

All results are simulation-based. The manuscript makes no claims about
measured energy, cost, security, privacy, or deployment performance.
