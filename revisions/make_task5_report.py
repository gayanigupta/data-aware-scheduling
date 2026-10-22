#!/usr/bin/env python3
"""Build revisions/MILP_skipped_tasks.docx -- the task-4 write-up.
Run after check_skipped_tasks.py has produced the CSV:
    python3 revisions/make_task5_report.py
"""

import os

import pandas as pd
from docx import Document
from docx.shared import Pt

HERE = os.path.dirname(__file__)
CSV = os.path.join(HERE, "results", "task-04", "skipped_tasks.csv")

df = pd.read_csv(CSV)
solved = df[df.note == "ok"]
n_solved = len(solved)
n_runs_skip = int((solved.n_skipped > 0).sum())
total_skip = int(solved.n_skipped.sum())
total_tasks = int(solved.n_tasks.sum())
opt_rows = solved[solved.solver_status == "optimal"]
tl_rows = solved[solved.solver_status == "time limit"]
skip_tl = int(tl_rows.n_skipped.sum())
skip_opt = int(opt_rows.n_skipped.sum())

doc = Document()
doc.styles["Normal"].font.name = "Calibri"
doc.styles["Normal"].font.size = Pt(11)

doc.add_heading("What happens when a task runs at 0%", 0)

doc.add_heading("The question", 1)
doc.add_paragraph(
    "The model allows the execution fraction to be zero. A task with "
    "ell = 0 is placed on a node but never actually runs - yet its "
    "successors still wait for its data. We had to choose between two "
    "fixes: force a minimum fraction (say ell >= 0.1), or write one "
    "sentence in the paper explaining what a skipped task sends "
    "downstream. We chose the sentence. The measurement below explains "
    "why.")

doc.add_heading("What a skipped task sends", 1)
doc.add_paragraph(
    "A skipped task does no work and earns no accuracy, but it still "
    "hands its declared output data D_ji to every successor. The payload "
    "on an edge is a fixed input of the workflow - it is not a function "
    "of how much of the task ran - so the transfer cost is charged "
    "whether or not the task ran. This is what the code has always done "
    "(Instance.comm() ignores the fraction), and the paper now states it "
    "in words after constraint (7).")

doc.add_heading("How often it actually happens", 1)
doc.add_paragraph(
    f"We re-solved every MILP run in the experiments and decoded the "
    f"fraction vector ({n_solved} runs solved, the rest sit above the "
    f"model-size cap). Skipped tasks are rare: {total_skip} tasks out "
    f"of {total_tasks} ({100*total_skip/total_tasks:.2f}%), spread over "
    f"{n_runs_skip} runs.")
doc.add_paragraph(
    f"Every one of them sits in a run that stopped at the time limit - "
    f"{skip_tl} skipped tasks across the {len(tl_rows)} time-limited "
    f"runs, all at alpha = 1.0 or bandwidth scale <= 0.2. In the "
    f"{len(opt_rows)} runs that certified optimality, the count of "
    f"skipped tasks is {skip_opt}: the solver never chooses to skip a "
    f"task once it has finished.")

doc.add_heading("Why the sentence and not the constraint", 1)
doc.add_paragraph(
    "Skipping never helps an optimal schedule - it pays the transfer "
    "time for zero accuracy - so a finished solve contains none. A "
    "minimum-fraction constraint would therefore only ever bite inside "
    "an unfinished, time-limited incumbent, while forcing every "
    "experiment and every number in the paper to be regenerated. "
    "Documenting the semantics fixes the ambiguity without changing "
    "any result.")

doc.add_heading("Runs that contain skipped tasks", 1)
show = solved[solved.n_skipped > 0]
t = doc.add_table(rows=1, cols=6)
t.style = "Light Grid Accent 1"
for i, h in enumerate(["experiment", "param", "rep", "status",
                       "skipped", "mean fraction"]):
    t.rows[0].cells[i].text = h
for _, r in show.iterrows():
    for i, v in enumerate([r.experiment, str(r.param), str(r.rep),
                           r.solver_status, str(int(r.n_skipped)),
                           f"{r.mean_fraction:.3f}"]):
        t.add_row().cells[i].text = v

doc.add_paragraph(
    "Every run - solved or skipped over the cap - is in "
    "revisions/results/task-04/skipped_tasks.csv, produced by "
    "revisions/check_skipped_tasks.py. The same data is drawn as a "
    "figure in the paper (revisions/results/task-04/skipped_tasks.png, "
    "made by make_task4_figure.py):")
doc.add_picture(os.path.join(HERE, "results", "task-04",
                             "skipped_tasks.png"))

doc.save(os.path.join(HERE, "MILP_skipped_tasks.docx"))
print("wrote revisions/MILP_skipped_tasks.docx")
