#!/usr/bin/env python3
"""Build revisions/MILP_vs_heuristic_analysis.docx -- the write-up of the
'heuristic beats MILP' investigation, with the figures embedded.
Run from the repo root:  python3 revisions/make_report.py
"""

import os

from docx import Document
from docx.shared import Inches, Pt

ROOT = os.path.join(os.path.dirname(__file__), "..")
FIG = os.path.join(ROOT, "data", "results", "figures")

doc = Document()
doc.styles["Normal"].font.name = "Calibri"
doc.styles["Normal"].font.size = Pt(11)

doc.add_heading("Why a heuristic sometimes scored above the MILP", 0)
doc.add_paragraph(
    "The figures in the paper contain a few points where a heuristic "
    "method appears to score higher than the MILP. Since the MILP solves "
    "the model exactly, a heuristic should never beat it on the same "
    "problem, so this needed an explanation. This note lists every such "
    "case, reruns the MILP on the same instances, and identifies the "
    "cause. All numbers below come from the result files in "
    "data/results/ and from the diagnostic reruns stored in this folder "
    "(diagnose_milp_gap.py, fix_flagged_milp.py, milp_diagnostics.csv).")

doc.add_paragraph(
    "A quick note on terms. Each experiment in the paper varies one "
    "setting at a time - deadline slack, number of fog nodes, workflow "
    "size, failure rate, or link bandwidth. For each setting we run five "
    "repetitions, each on a freshly generated problem instance. The "
    "generator uses a fixed random seed for each repetition (seeds 0, "
    "1000, 2000, 3000, 4000), so asking for the same settings always "
    "produces the identical instance. In the tables below, 'rep' means "
    "which of the five repetitions a row belongs to.")

doc.add_heading("1. Points where a heuristic scored higher", 1)
doc.add_paragraph(
    "In the deadline-slack figure (Figure 4) and the federation-size "
    "figure (Figure 5), a few points place the greedy marker slightly "
    "above the MILP marker. The figures show averages, so I went back to "
    "the raw result files and compared methods instance by instance. "
    "Every case where a directly comparable method scored above the MILP "
    "on the same instance is listed here:")

t = doc.add_table(rows=1, cols=5)
t.style = "Light Grid Accent 1"
for i, h in enumerate(["Experiment", "Setting", "Rep", "Greedy", "MILP"]):
    t.rows[0].cells[i].text = h
for r in [
    ("deadline slack (Fig. 4)", "alpha = 1.2", "2", "1.4422", "1.4383"),
    ("deadline slack (Fig. 4)", "alpha = 1.2", "3", "1.4226", "1.4040"),
    ("deadline slack (Fig. 4)", "alpha = 1.2", "4", "1.4515", "1.4481"),
    ("deadline slack (Fig. 4)", "alpha = 1.3", "3", "1.4226", "1.4165"),
    ("deadline slack (Fig. 4)", "alpha = 1.5", "1", "1.4370", "1.4369"),
    ("federation size (Fig. 5)", "N = 10", "0", "1.3464", "1.3412"),
    ("federation size (Fig. 5)", "N = 10", "3", "1.4044", "1.4043"),
    ("workflow size (Fig. 6)", "n = 100", "4", "1.4322", "1.4276"),
    ("task failures (Fig. 7)", "all rates", "1", "1.4370", "1.4369"),
    ("link bandwidth (Fig. 8)", "scale = 1.0", "1", "1.4370", "1.4369"),
    ("link bandwidth (Fig. 8)", "scale = 0.2", "4", "1.4515", "1.4207"),
]:
    for i, v in enumerate(r):
        t.add_row().cells[i].text = v

doc.add_paragraph(
    "Two things in this list need a word of explanation. The failure "
    "experiment entry at repetition 1 shows up at all six failure rates "
    "because every rate is tested on the same generated instance - it is "
    "one instance, not six. That same default instance is also behind "
    "the slack alpha = 1.5 repetition-1 row and the bandwidth scale = "
    "1.0 repetition-1 row. Separately, the bandwidth-blind baseline also "
    "scores above the MILP at heavily degraded bandwidths, but it is not "
    "a fair comparison - that baseline picks its placements as if "
    "transfers were free - so it is left out of this list.")

doc.add_picture(os.path.join(FIG, "perf_slack_accuracy.png"),
                width=Inches(5.5))
doc.add_paragraph("Figure 4 (deadline slack), regenerated after the fix.")
doc.add_picture(os.path.join(FIG, "perf_nodes_accuracy.png"),
                width=Inches(5.5))
doc.add_paragraph("Figure 5 (federation size), regenerated after the fix.")

doc.add_heading("2. Rerunning the MILP on the flagged instances", 1)
doc.add_paragraph(
    "For each case in the table, I regenerated the instance exactly as "
    "the experiment had built it and solved the MILP twice: once with "
    "the original 60-second time limit, and once with a 300-second "
    "limit. For every solve I recorded the solver status (whether it "
    "proved optimality or stopped at the time limit), the actual "
    "runtime, and the final score.")

t2 = doc.add_table(rows=1, cols=7)
t2.style = "Light Grid Accent 1"
for i, h in enumerate(["Point", "60 s status", "60 s time", "60 s score",
                       "300 s status", "300 s score", "Greedy"]):
    t2.rows[0].cells[i].text = h
for r in [
    ("slack 1.2 rep 2", "time limit", "60.6 s", "1.4383",
     "optimal", "1.4422", "1.4422"),
    ("slack 1.2 rep 3", "time limit", "60.6 s", "1.4040",
     "optimal", "1.4226", "1.4226"),
    ("slack 1.2 rep 4", "time limit", "60.6 s", "1.4481",
     "optimal", "1.4515", "1.4515"),
    ("slack 1.3 rep 3", "time limit", "60.6 s", "1.4156",
     "optimal", "1.4226", "1.4226"),
    ("slack 1.5 rep 1", "optimal", "0.7 s", "1.4369",
     "optimal", "1.4370*", "1.4370"),
    ("nodes 10 rep 0", "time limit", "61.4 s", "1.3412",
     "optimal", "1.3464", "1.3464"),
    ("nodes 10 rep 3", "optimal", "35.5 s", "1.4043",
     "optimal", "1.4044*", "1.4044"),
    ("size 100 rep 4", "time limit", "61.4 s", "1.4276",
     "optimal", "1.4322", "1.4322"),
    ("bandwidth 0.2 rep 4", "time limit", "60.5 s", "1.4207",
     "optimal", "1.4515", "1.4515"),
]:
    for i, v in enumerate(r):
        t2.add_row().cells[i].text = v

doc.add_paragraph(
    "* These two solves needed a tighter stopping rule than the default. "
    "The solver stops when the best solution found is provably within a "
    "small fraction of the true optimum - by default 1e-4 (0.01%). On "
    "these instances it stopped with a solution about 1e-4 below the "
    "bound, which was just enough to show up as 'below the greedy'. "
    "Tightening the rule to 1e-6 (0.0001%) pushed the result up to the "
    "bound.")

doc.add_heading("3. Checking that the same instances were used", 1)
doc.add_paragraph(
    "The experiments do not load instances from files - each repetition "
    "generates its instance on the spot from the seed, and all four "
    "methods are run on that one generated object. So by construction "
    "they could not have seen different data. To be extra sure that my "
    "reruns rebuilt the same instances the sweeps had used, I compared "
    "each rebuilt instance's accuracy bound (the score obtained when "
    "every task runs in full) against the bound recorded in the result "
    "files. On all nine flagged instances the bounds matched to nine "
    "decimal places. The differences are therefore not explained by "
    "methods seeing different instances.")
doc.add_paragraph(
    "I also checked the per-dataset test runs in test_runs.csv. On "
    "those fixed datasets the MILP never scores below any other method: "
    "on the small and medium datasets it sits on the bound together "
    "with the greedy.")

doc.add_heading("4. What caused it", 1)
doc.add_paragraph(
    "The answer is two numerical effects inside the solver, not a bug in "
    "the model and not a difference between instances.")
doc.add_paragraph(
    "The main effect is the time limit. Eight of the nine flagged MILP "
    "runs stopped because their 60 seconds ran out, not because they "
    "had finished. In each of those runs the solver still had an open "
    "gap - between 0.2% and 2.2% - between the best schedule it had "
    "found and the best it could prove exists. In other words, the "
    "number recorded in the table was the best answer found so far, "
    "not the best answer. Given 300 seconds, every one of those "
    "instances was solved to proven optimality, and the score landed "
    "exactly on the bound - level with the greedy, never below it.")
doc.add_paragraph(
    "The second effect is the solver's stopping tolerance. In two runs "
    "the solver genuinely declared the solution 'optimal', but its "
    "stopping rule allows the certified answer to be within 0.01% of "
    "the true optimum. The recorded score sat about that much below the "
    "bound - small enough to look like a tie, but technically below the "
    "greedy score in the table. Tightening the tolerance to 0.0001% "
    "closed that hairline gap.")

doc.add_heading("5. What was changed", 1)
doc.add_paragraph(
    "Every instance where the MILP had finished below another method "
    "was re-solved with a 300-second limit and the tighter stopping "
    "rule (the script is revisions/fix_flagged_milp.py). The corrected "
    "scores, runtimes, and feasibility flags were written back into the "
    "five result files (slack, nodes, size, failure, bandwidth), and "
    "all five experiment figures were regenerated from the updated "
    "data and copied into the paper's Figures folder.")
doc.add_paragraph(
    "After the update, scanning every result file confirms that no "
    "instance remains where rounding, the greedy, or the genetic "
    "algorithm scores above the MILP. In the slack experiment the MILP "
    "now sits exactly on the bound from alpha = 1.2 upward, as does the "
    "greedy. The federation-size and workflow-size figures changed the "
    "same way - the MILP marker now lies on the bound everywhere the "
    "text claimed it did.")

doc.add_heading("6. What changed in the paper", 1)
doc.add_paragraph(
    "The experimental setup now states both limits: the MILP is first "
    "solved with a 60-second time limit, and any run that finished "
    "below a heuristic was re-solved with a 300-second limit and the "
    "tighter tolerance, with the certified scores being the ones "
    "reported. The slack-results paragraph now says the MILP reaches "
    "the bound from alpha = 1.2 onward, matching the regenerated "
    "figure. The limitations paragraph and the companion notebook were "
    "updated to document this re-solve step. Visually, the only change "
    "a reader will notice is in the deadline-slack figure: the MILP "
    "curve no longer sits a hair below the bound at the middle slack "
    "values - it lies on it.")

doc.save(os.path.join(os.path.dirname(__file__),
                      "MILP_vs_heuristic_analysis.docx"))
print("wrote revisions/MILP_vs_heuristic_analysis.docx")
