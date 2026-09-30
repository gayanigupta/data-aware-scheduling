# Data

## `instances/`

Generated scheduling instances in JSON. Each file contains:

| Field | Meaning |
|---|---|
| `t` | full execution time of task i on node a (n × m) |
| `A` | per-task accuracy weight (n) |
| `D` | data size of DAG edge (j → i); 0 if absent (n × n) |
| `B` | bandwidth of link (b, a); diagonal 0 = co-located (m × m) |
| `P` | eligibility: 1 if task i may run on node a (n × m) |
| `t_max` | workflow deadline (= slack factor × optimistic critical path) |

File names encode the generator parameters:
`dag<tasks>_nodes<nodes>_a<alpha>_s<seed>.json`.

Regenerate with:

```bash
python3 code/fogsim.py gen --tasks 50 --nodes 5 --alpha 1.5 --seed 0
```

## `results/`

Per-run sweep outputs written by `python3 code/fogsim.py sweep <kind>`
(`slack`, `nodes`, `size`, `failure`), one CSV per sweep:

| Column | Meaning |
|---|---|
| `param` | swept value (slack α, node count, task count, failure rate) |
| `method` | `milp` / `rounding` / `greedy` / `ga` |
| `score` | average accuracy score (1/n)·Σ A_i·ℓ_i |
| `makespan`, `feasible`, `runtime_s` | schedule length, deadline met, wall time |

`results/figures/` holds plots rendered from the CSVs by
`python3 code/fogsim.py plot`. These re-run figures are a reproduction of
the paper's experimental protocol, not the original plotted data.
