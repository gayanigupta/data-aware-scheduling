"""Build the conference slide deck for the federated-fog scheduling paper.

Generates slides/presentation.pptx from paper content + generated figures.
Run from the repo root:  python3 code/make_slides.py
"""
import os

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "paper", "Figures")
OUT = os.path.join(ROOT, "slides", "data-aware-scheduling.pptx")

NAVY = RGBColor(0x0D, 0x2C, 0x54)
GREY = RGBColor(0x55, 0x55, 0x55)
DARK = RGBColor(0x21, 0x21, 0x21)

prs = Presentation()
prs.slide_width = Inches(13.333)   # 16:9
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def add_slide(title=None):
    s = prs.slides.add_slide(BLANK)
    if title:
        bar = s.shapes.add_textbox(Inches(0.5), Inches(0.25),
                                 Inches(12.3), Inches(0.8))
        tf = bar.text_frame
        tf.text = title
        p = tf.paragraphs[0]
        p.font.size = Pt(30)
        p.font.bold = True
        p.font.color.rgb = NAVY
    return s


def bullets(slide, items, left=0.6, top=1.2, width=7.0, height=5.8,
            size=18):
    box = slide.shapes.add_textbox(Inches(left), Inches(top),
                                   Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    first = True
    for level, text in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.text = ("  " * level) + text
        p.level = level
        p.font.size = Pt(size if level == 0 else size - 2)
        p.font.color.rgb = DARK if level == 0 else GREY
        p.space_after = Pt(8)
    return box


def pic(slide, path, left, top, width=None, height=None):
    kw = {}
    if width: kw["width"] = Inches(width)
    if height: kw["height"] = Inches(height)
    slide.shapes.add_picture(os.path.join(FIG, path),
                             Inches(left), Inches(top), **kw)


def caption(slide, text, left, top, width):
    box = slide.shapes.add_textbox(Inches(left), Inches(top),
                                   Inches(width), Inches(0.6))
    p = box.text_frame.paragraphs[0]
    p.text = text
    p.font.size = Pt(12)
    p.font.italic = True
    p.font.color.rgb = GREY
    p.alignment = PP_ALIGN.CENTER


# ---------- 1. Title ----------
s = add_slide()
t = s.shapes.add_textbox(Inches(1), Inches(1.6), Inches(11.3), Inches(2.2))
p = t.text_frame.paragraphs[0]
p.text = ("Data-Aware Scheduling of Approximate DAG Workflows\n"
          "in Federated Fog Systems")
p.font.size = Pt(36); p.font.bold = True; p.font.color.rgb = NAVY
p.alignment = PP_ALIGN.CENTER
a = s.shapes.add_textbox(Inches(1), Inches(4.2), Inches(11.3), Inches(1.8))
tf = a.text_frame; tf.word_wrap = True
p = tf.paragraphs[0]
p.text = ("Gayani Gupta, Amisha Gupta, Mohsen Amini Salehi,\n"
          "Antonio Fernandez Anta, Sanjukta Bhowmick, Jose Aguilar")
p.font.size = Pt(20); p.alignment = PP_ALIGN.CENTER
p2 = tf.add_paragraph()
p2.text = ("University of North Texas | UC Berkeley | IMDEA Networks | "
           "Universidad de Los Andes")
p2.font.size = Pt(14); p2.font.color.rgb = GREY
p2.alignment = PP_ALIGN.CENTER
p3 = tf.add_paragraph()
p3.text = "github.com/gayanigupta/data-aware-scheduling"
p3.font.size = Pt(14); p3.font.color.rgb = GREY
p3.alignment = PP_ALIGN.CENTER

# ---------- 2. Motivation ----------
s = add_slide("Motivation: disaster response without the cloud")
bullets(s, [
    (0, "Flood forecasting, wildfire tracking, evacuation planning "
        "run as workflows of dependent tasks"),
    (0, "During an extreme event the cloud link often fails - the work "
        "must happen on fog computers near the disaster area"),
    (0, "One fog site rarely has enough capacity to finish in time"),
    (0, "Nearby sites keep fast, stable links to each other - a "
        "federation of fog sites acts as a small local cloud"),
    (0, "The question: where should each task run, and how much of it "
        "should run, so the workflow finishes on time with the best "
        "possible accuracy?"),
])
pic(s, "federated-fog-architecture.png", 7.7, 1.3, width=5.2)
caption(s, "Federated fog deployment for disaster response", 7.7, 6.3, 5.2)

# ---------- 3. Two levers ----------
s = add_slide("What makes the scheduling hard")
bullets(s, [
    (0, "Lever 1 - data movement: a task's input can take as long to "
        "arrive as the task takes to run"),
    (1, "edge (Tj, Ti) carries D_ji bytes over link bandwidth B_ba"),
    (1, "a 'fast' remote node can lose more time to transfer than it "
        "saves in execution"),
    (0, "Lever 2 - approximate execution: tasks can run partially"),
    (1, "fraction l of a task costs l of its time and returns l of "
        "its accuracy"),
    (1, "at a tight deadline, 80% accuracy beats a missed alert"),
    (0, "Existing schedulers are compute-centric: they ignore one or "
        "both levers"),
])
pic(s, "disaster-response-dag.png", 8.0, 1.4, width=4.9)
caption(s, "Example disaster-response workflow (DAG)", 8.0, 6.2, 4.9)

# ---------- 4. Model ----------
s = add_slide("The model as an MILP")
bullets(s, [
    (0, "Decisions: assignment e_ia (binary), execution fraction "
        "l_ia, implied start times M_ia"),
    (0, "Objective: maximize average accuracy (1/n) sum_i A_i sum_a l_ia"),
    (0, "Constraints: each task on exactly one eligible node; a task "
        "starts only after every predecessor finishes AND its data "
        "arrives over the link"),
    (0, "Completion y_i = sum_a e_ia (M_ia + t_ia l_ia) <= deadline "
        "t_max for every task"),
    (0, "Jointly treats per-edge data size, per-link bandwidth, and "
        "per-task execution fraction - not previously combined in this "
        "setting"),
    (0, "NP-hard already on unrelated parallel machines - so the MILP "
        "is the benchmark, and we add three scalable schedulers"),
], width=12.0)

# ---------- 5. Three scalable schedulers ----------
s = add_slide("Three scalable schedulers on the same cost model")
bullets(s, [
    (0, "LP relaxation + randomized rounding"),
    (1, "relax e_ia to [0,1], sample each task's node from the LP "
        "solution, re-solve the LP for fractions"),
    (0, "Bandwidth/data-aware greedy"),
    (1, "priority = beta*A_i + (1-beta)*critical-path; earliest-finish "
        "node among ready tasks; retry with lower global fraction if "
        "the deadline is missed"),
    (0, "Genetic algorithm"),
    (1, "chromosome = assignment vector + per-task fractions; fitness "
        "rewards accuracy and penalizes deadline violations; "
        "co-location repair for heavy edges"),
    (0, "All three evaluate the same communication cost, so all are "
        "bandwidth-aware"),
], width=12.0)

# ---------- 6. Setup ----------
s = add_slide("Experimental setup")
bullets(s, [
    (0, "Discrete-event simulator (NumPy/SciPy HiGHS); synthetic "
        "disaster-response DAGs"),
    (0, "Parameters chosen so transfers are contested: t in [1,5], "
        "D in [5,50], B in [10,100]"),
    (0, "Four datasets: 10/3, 100/5, 500/8, 1000/10 tasks-nodes; "
        "structural DAGs up to 10^6 tasks in the notebook"),
    (0, "Five sweeps: deadline slack, federation size, workflow size, "
        "failure rate (retry-once), link-bandwidth degradation"),
    (0, "Baselines: fixed scheduling and the max-accuracy bound "
        "(dashed line in every plot); a bandwidth-blind greedy for "
        "the link sweep"),
    (0, "Metric: average achieved accuracy vs the bound; plus "
        "makespan, feasibility, wall time"),
], width=6.8)
pic(s, "dataset_medium_graphs.png", 7.6, 1.3, width=5.4)
caption(s, "A generated test dataset (medium, 100 tasks / 5 nodes)",
        7.6, 6.5, 5.4)

# ---------- 7. Results: slack ----------
s = add_slide("Deadline slack: the choice matters when it barely fits")
pic(s, "perf_slack_accuracy.png", 0.8, 1.1, width=6.6)
bullets(s, [
    (0, "At alpha = 1.0: MILP 1.38 vs bound 1.43; rounding 1.25, "
        "greedy 1.23, GA 1.20"),
    (0, "From alpha = 1.2 the greedy reaches the bound; the MILP "
        "follows at 1.5"),
    (0, "Rounding and the GA never fully close the gap even at loose "
        "slack - a fixed sampling budget does not recover the bound"),
], left=7.7, width=5.0)

# ---------- 8. Results: federation size ----------
s = add_slide("Federation size: capacity buys feasibility, not accuracy")
pic(s, "perf_nodes_accuracy.png", 0.8, 1.1, width=6.6)
bullets(s, [
    (0, "MILP and greedy match the bound at every N"),
    (0, "GA drifts from ~1.5% below the bound (N=2) to ~8% (N=10); "
        "rounding matches only at N=2, ~8% short at N=10"),
    (0, "Fixed search budgets cover a shrinking fraction of the "
        "placement space as N grows"),
    (0, "Extra nodes do not raise accuracy once the deadline is met - "
        "their value is the feasible placements they open"),
], left=7.7, width=5.0)

# ---------- 9. Results: workflow size ----------
s = add_slide("Workflow size: the simple greedy holds up best")
pic(s, "perf_task_size_accuracy.png", 0.8, 1.1, width=6.6)
bullets(s, [
    (0, "n = 10 / 100: MILP and greedy on the bound; GA first to "
        "drift (1.26 at 100)"),
    (0, "n = 1000: MILP beyond the 800-variable cap; greedy stays on "
        "the bound in 0.15 s"),
    (0, "Rounding 1.37 but ~93 s per LP re-solve; GA falls to 1.10 "
        "in 159 s"),
    (0, "The GA's fixed budget is spread over a combinatorially "
        "growing space - size-adaptive budgets would close the gap"),
], left=7.7, width=5.0)

# ---------- 10. Results: failures ----------
s = add_slide("Task failures: methods separate on feasibility")
pic(s, "perf_failure_accuracy.png", 0.8, 1.1, width=6.6)
bullets(s, [
    (0, "Retry-once model: a failed task reruns in place; accuracy is "
        "kept if the retry meets the deadline"),
    (0, "Scores are flat - retries preserve accuracy"),
    (0, "Feasibility separates them: greedy 100% at every rate; "
        "MILP and GA ~60%; rounding ~20%"),
    (0, "Flat-vs-rate: at n = 100 tasks even a 10% rate makes at "
        "least one failure almost certain"),
], left=7.7, width=5.0)

# ---------- 11. Results: bandwidth ----------
s = add_slide("Link degradation: what data-aware placement is worth")
pic(s, "perf_bandwidth_accuracy.png", 0.8, 1.1, width=6.6)
bullets(s, [
    (0, "Bandwidth-blind greedy reports bound-level scores but misses "
        "the deadline: 80% feasible at 0.5x, 20% at 0.2x, 0% below"),
    (0, "MILP stays feasible at every level, losing ~10% of score at "
        "0.05x"),
    (0, "Greedy stays feasible to 0.1x but pays in accuracy (0.80); "
        "GA holds to 0.1x, fails at 0.05x"),
    (0, "Rounding survives only above 0.5x in our implementation"),
], left=7.7, width=5.0)

# ---------- 12. Takeaways ----------
s = add_slide("Takeaways")
bullets(s, [
    (0, "The scheduler matters most exactly where the deadline binds"),
    (0, "Accuracy under a binding deadline is not free in wall time: "
        "greedy 0.15 s vs rounding ~372 s vs GA ~159 s at n = 1000"),
    (0, "Data-aware placement is what keeps schedules feasible as "
        "links degrade - the blind baseline's 'perfect' scores are "
        "late schedules"),
    (0, "Honest limits: MILP capped at 800 assignment vars; LP rows "
        "grow ~10^5 at n=1000; fixed GA budget degrades; dense n x n "
        "instances stop at ~10^4 tasks (10^6 structural only)"),
], width=12.0)

# ---------- 13. Conclusion ----------
s = add_slide("Conclusion and future work")
bullets(s, [
    (0, "One joint formulation: placement + execution fraction + "
        "data movement, verified with proofs and a solver-ready "
        "linearization"),
    (0, "Four schedulers, one cost model; sweeps over slack, size, "
        "federation, failures, and bandwidth"),
    (0, "Next: sparse/decomposed formulations toward 10^6-task "
        "instances; adaptive GA budgets; replication/checkpointing "
        "beyond retry-once; online re-scheduling on a real testbed"),
    (0, "Reproduce: github.com/gayanigupta/data-aware-scheduling "
        "- code, data, executed notebook"),
], width=12.0)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
prs.save(OUT)
print("wrote", OUT, f"({len(prs.slides.__iter__.__self__._sldIdLst)} slides)")
