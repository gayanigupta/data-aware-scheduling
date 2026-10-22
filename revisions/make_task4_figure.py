#!/usr/bin/env python3
"""Task 4 -- chart: skipped tasks (ell = 0) occur only in time-limited runs.

Reads revisions/results/task-04/skipped_tasks.csv (produced by
check_skipped_tasks.py) and draws a bar chart of skipped tasks per
experiment setting, summed over the five repetitions.  All settings not
shown have zero skipped tasks.

Output: revisions/results/task-04/skipped_tasks.png
Run from the repo root:  python3 revisions/make_task4_figure.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = os.path.dirname(__file__)
CSV = os.path.join(HERE, "results", "task-04", "skipped_tasks.csv")
OUT = os.path.join(HERE, "results", "task-04", "skipped_tasks.png")

df = pd.read_csv(CSV)
solved = df[df.note == "ok"]

by_set = (solved.groupby(["experiment", "param"])["n_skipped"]
          .sum().reset_index())
by_set = by_set[by_set.n_skipped > 0]
by_set["param"] = by_set.param.astype(float)

labels = []
for _, r in by_set.iterrows():
    if r.experiment == "slack":
        labels.append("slack\n" + r"$\alpha$=" + f"{r.param:g}")
    else:
        labels.append(f"bw\n{r.param:g}x")
# order: slack first, then bandwidth by decreasing scale
order = sorted(range(len(by_set)),
               key=lambda k: (by_set.experiment.iloc[k] != "slack",
                              -by_set.param.iloc[k]))
by_set = by_set.iloc[order]
labels = [labels[k] for k in order]

fig, ax = plt.subplots(figsize=(3.6, 2.8), dpi=300)
bars = ax.bar(range(len(by_set)), by_set.n_skipped,
              color="#0d2c54", width=0.6)
for b, v in zip(bars, by_set.n_skipped):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.4, str(int(v)),
            ha="center", fontsize=10, fontweight="bold")
ax.set_xticks(range(len(by_set)))
ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel("skipped tasks  ($\\ell_i=0$)", fontsize=11)
ax.tick_params(labelsize=10)
ax.grid(axis="y", alpha=0.3, lw=0.5)
ax.set_ylim(0, by_set.n_skipped.max() * 1.45)
ax.text(0.03, 0.96, "zero in all other settings\nand in every certified-optimal run",
        transform=ax.transAxes, ha="left", va="top", fontsize=8.5,
        fontstyle="italic", color="#555555")
fig.tight_layout()
fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("wrote", OUT)
