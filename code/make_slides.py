"""Build the conference slide deck for the federated-fog scheduling paper.

Generates slides/data-aware-scheduling.pptx — a ~20-slide talk that tells
the paper's story end to end, with speaker notes on every slide.
Run from the repo root:  python3 code/make_slides.py
"""
import os

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "paper", "Figures")
RES = os.path.join(ROOT, "data", "results")
OUT = os.path.join(ROOT, "slides", "data-aware-scheduling.pptx")

NAVY = RGBColor(0x0D, 0x2C, 0x54)
GREY = RGBColor(0x55, 0x55, 0x55)
DARK = RGBColor(0x21, 0x21, 0x21)
ACCENT = RGBColor(0xB0, 0x3A, 0x2E)

prs = Presentation()
prs.slide_width = Inches(13.333)   # 16:9
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def add_slide(title=None, notes=None):
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
    if notes:
        s.notes_slide.notes_text_frame.text = notes
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


def pic(slide, path, left, top, width=None, height=None, base=FIG):
    kw = {}
    if width: kw["width"] = Inches(width)
    if height: kw["height"] = Inches(height)
    slide.shapes.add_picture(os.path.join(base, path),
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


# =====================================================================
# ACT I — THE SETTING
# =====================================================================

# ---------- 1. Title ----------
s = add_slide(notes=(
    "Welcome everyone. This talk is about scheduling workflows on "
    "federated fog systems when the cloud is out of reach — think "
    "disaster response. The story: the problem, the model, four "
    "schedulers, five experiments, and what we learned."))
t = s.shapes.add_textbox(Inches(1), Inches(1.5), Inches(11.3), Inches(2.2))
p = t.text_frame.paragraphs[0]
p.text = ("Data-Aware Scheduling of Approximate DAG Workflows\n"
          "in Federated Fog Systems")
p.font.size = Pt(36); p.font.bold = True; p.font.color.rgb = NAVY
p.alignment = PP_ALIGN.CENTER
a = s.shapes.add_textbox(Inches(1), Inches(4.0), Inches(11.3), Inches(2.2))
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

# ---------- 2. Scenario ----------
s = add_slide("The scenario", notes=(
    "Picture a river basin flooding. A workflow runs: rainfall "
    "sensors feed a runoff model, that feeds a flood-forecast model, "
    "that feeds evacuation planning and public alerts. Every stage "
    "hands data to the next. The deadline is not soft — a forecast "
    "that arrives after the water is useless. Now: during the storm, "
    "the uplink to the cloud is degraded or dead. The compute must "
    "happen on machines close to the disaster area."))
bullets(s, [
    (0, "A disaster unfolds: flood, wildfire, offshore incident"),
    (0, "Response systems run workflows of dependent tasks"),
    (1, "sense -> model -> predict -> plan -> alert"),
    (1, "each stage hands data to the next"),
    (0, "The deadline is hard: a forecast that arrives late is a "
        "forecast nobody uses"),
    (0, "Meanwhile the uplink to the cloud is degraded or gone"),
    (0, "So the computation must run on fog computers near the "
        "disaster area"),
], width=12.0)

# ---------- 3. Federation ----------
s = add_slide("One fog site is not enough — so sites federate", notes=(
    "A single fog site — a cell-tower rack, a roadside cabinet, a "
    "ship's server — rarely has the capacity to run the whole "
    "workflow in time. But several nearby sites share fast local "
    "links. Federating them gives a small local cloud. The catch: "
    "now every task has a choice of where to run, and that choice "
    "has a price — the data has to move."))
bullets(s, [
    (0, "Fog sites near the event: cell-tower racks, roadside "
        "cabinets, platform servers"),
    (0, "Individually too weak; but they keep fast, stable links to "
        "each other even when the cloud link fails"),
    (0, "Federation = a small local cloud built from nearby sites"),
    (0, "The catch: every task can now run in many places —"),
    (1, "and wherever it runs, its input data has to get there first"),
], width=6.9)
pic(s, "federated-fog-architecture.png", 7.7, 1.3, width=5.2)
caption(s, "Federated fog deployment around a disaster area",
        7.7, 6.3, 5.2)

# ---------- 4. The workflow ----------
s = add_slide("The workflow is a DAG — and data is the glue", notes=(
    "The workflow is a directed acyclic graph: tasks are nodes, "
    "dependencies are edges. On each edge rides a chunk of data — "
    "tens of units in our model, which at realistic link speeds can "
    "take as long to move as the task itself takes to run. That is "
    "the first lever. The second: many of these tasks are iterative "
    "models — a hydrology model, a tracker — that can run partially "
    "and still return something useful."))
bullets(s, [
    (0, "Tasks = nodes, dependencies = edges (a DAG)"),
    (0, "Every edge carries data, D_ji, across a link of bandwidth B"),
    (1, "transfer time = D_ji / B  —  comparable to task runtime"),
    (0, "Tasks are approximate: running a fraction l costs l of the "
        "time and returns l of the accuracy"),
    (1, "a flood model at 80% fidelity still warns in time"),
], width=6.6)
pic(s, "disaster-response-dag.png", 7.4, 1.2, width=5.5)
caption(s, "Example disaster-response DAG used in the study",
        7.4, 6.4, 5.5)

# ---------- 5. The problem ----------
s = add_slide("The problem, in one sentence", notes=(
    "So the problem is: place every task on a node, choose how much "
    "of each task to run, so that the whole DAG finishes before the "
    "deadline and the average accuracy is as high as possible. Two "
    "things make it interesting. First, data movement is a "
    "first-class cost — the fastest node for a task can be the worst "
    "choice once you pay for shipping its input. Second, accuracy is "
    "a knob, not a constant — when the deadline is tight you can buy "
    "time by giving back some accuracy."))
bullets(s, [
    (0, "Assign every task to a fog node AND choose how much of it "
        "to run,"),
    (0, "so that the DAG finishes before the deadline"),
    (0, "with the highest possible average accuracy."),
    (0, ""),
    (0, "Why it is hard:"),
    (1, "data transfer time rivals execution time — the 'fastest' "
        "node can be the worst once you pay to move the input"),
    (1, "accuracy is a tradeable resource — tight deadline? run "
        "partially, arrive on time"),
    (1, "the two choices interact: placement decides transfers, "
        "fractions decide runtimes"),
], width=12.0)

# ---------- 6. Prior work gap ----------
s = add_slide("Why existing schedulers do not fit", notes=(
    "Classic DAG schedulers — HEFT is the standard reference — rank "
    "tasks and place each where it finishes earliest. They assume "
    "every task runs to completion and treat transfer time as a "
    "fixed edge weight. Fog schedulers mostly do capacity and "
    "placement, ignoring approximate execution. Nobody combines: "
    "per-edge data volume, per-link bandwidth, and a per-task "
    "execution fraction, under one deadline, on a federation."))
bullets(s, [
    (0, "HEFT (Heterogeneous Earliest Finish Time): the classic DAG "
        "scheduler"),
    (1, "ranks tasks, places each where it finishes earliest"),
    (1, "but: full execution only; transfers are static edge weights"),
    (0, "Fog schedulers handle capacity and placement — but assume "
        "tasks always run completely"),
    (0, "Approximate-computing work trades quality for time — but "
        "ignores inter-node data movement"),
    (0, "Our gap: jointly optimize placement + data movement + "
        "execution fraction under one deadline"),
], width=12.0)

# =====================================================================
# ACT II — THE MODEL AND THE ALGORITHMS
# =====================================================================

# ---------- 7. MILP ----------
s = add_slide("The formulation: one MILP", notes=(
    "Three decisions per task: which node (e_ia), what fraction "
    "(l_ia), when it starts (M_ia). The objective maximizes average "
    "accuracy. Constraints force each task onto exactly one eligible "
    "node, make a task wait for every predecessor to finish AND its "
    "data to arrive — that is where the D over B term enters — and "
    "keep every task's completion time inside the deadline. Deadline "
    "feasibility is the same bound used in the paper's proofs; the "
    "linearization is solver-ready."))
bullets(s, [
    (0, "Decisions: e_ia in {0,1} (task i on node a), l_ia in [0,1] "
        "(fraction), M_ia (start time)"),
    (0, "Objective: max (1/n) sum_i A_i sum_a l_ia — average accuracy"),
    (0, "One eligible node per task:  sum_a e_ia = 1"),
    (0, "Precedence + data: task i waits until every predecessor j "
        "finished AND D_ji/B_ba arrived"),
    (0, "Deadline: sum_a e_ia (M_ia + t_ia l_ia) <= t_max  for all i"),
    (0, "NP-hard even on unrelated parallel machines — the MILP is "
        "the benchmark, not the product"),
], width=12.0)

# ---------- 8. Algorithm portfolio ----------
s = add_slide("Four schedulers, one cost model", notes=(
    "Because the problem is NP-hard, we also built three scalable "
    "schedulers that all share the same communication-cost model — "
    "so any difference in the results is about the algorithm, not "
    "the accounting. Randomized rounding: solve the LP relaxation, "
    "sample each task's node from the fractional solution, re-solve "
    "the LP for the fractions. Greedy: priority order, earliest-"
    "finish placement, retry with smaller fractions if late. GA: "
    "chromosome encodes assignment plus fractions."))
bullets(s, [
    (0, "MILP (HiGHS) — optimal at small/medium scale; the benchmark"),
    (0, "LP relaxation + randomized rounding"),
    (1, "relax e_ia to [0,1]; sample each task's node from the LP; "
        "re-solve the LP for fractions"),
    (0, "Data-aware greedy"),
    (1, "priority = beta*A_i + (1-beta)*critical-path; earliest-finish "
        "node among ready tasks; on deadline miss, retry with a "
        "lower global fraction"),
    (0, "Genetic algorithm"),
    (1, "chromosome = assignment + per-task fractions; fitness "
        "rewards accuracy, penalizes lateness; co-location repair "
        "for heavy edges"),
], width=12.0)

# ---------- 9. Setup ----------
s = add_slide("How we test it", notes=(
    "A discrete-event simulator in Python — NumPy and SciPy's HiGHS "
    "solver. Parameters are chosen so the problem is contested: "
    "runtimes 1–5, edge payloads 5–50, link bandwidth 10–100 — so a "
    "transfer can genuinely rival a task. Four datasets from 10 "
    "tasks/3 nodes up to 1000 tasks/10 nodes. Five parameter sweeps. "
    "The yardstick in every plot: the max-accuracy bound — run "
    "everything fully — drawn as the dashed line. Plus a "
    "bandwidth-blind greedy in the link sweep to show what ignoring "
    "data costs."))
bullets(s, [
    (0, "Discrete-event simulator (NumPy + SciPy HiGHS)"),
    (0, "Contested regime: t in [1,5], D in [5,50], B in [10,100] — "
        "a transfer can rival a task"),
    (0, "Datasets: 10/3, 100/5, 500/8, 1000/10 tasks-nodes; ~15% of "
        "node-task pairs ineligible; ~2x node speed range"),
    (0, "Five sweeps: slack | federation size | workflow size | "
        "failure rate | link bandwidth"),
    (0, "Metric: average accuracy vs the max-accuracy bound (dashed "
        "line); plus feasibility and wall time"),
    (0, "Baselines: fixed scheduling; a bandwidth-blind greedy in "
        "the link sweep"),
], width=6.9)
pic(s, "dataset_medium_graphs.png", 7.6, 1.3, width=5.4, base=RES)
caption(s, "A generated dataset (100 tasks / 5 nodes)", 7.6, 6.5, 5.4)

# =====================================================================
# ACT III — FIVE EXPERIMENTS
# =====================================================================

# ---------- 10. Sweep overview ----------
s = add_slide("Five questions", notes=(
    "Each sweep varies one thing and holds the rest fixed. Slack: "
    "how tight is the deadline? Federation: how many nodes? "
    "Workflow: how many tasks? Failures: what if tasks crash and "
    "retry once? Bandwidth: what if the local links degrade? Five "
    "reps each, fresh random instances."))
bullets(s, [
    (0, "Q1  Deadline slack alpha in {1.0 ... 2.0} — how tight is "
        "the deadline?"),
    (0, "Q2  Federation size N in {2 ... 10} nodes — does capacity "
        "help?"),
    (0, "Q3  Workflow size n in {10, 100, 1000} — who scales?"),
    (0, "Q4  Failure rate in {0 ... 0.5}, retry-once — who stays "
        "feasible?"),
    (0, "Q5  Bandwidth x {1.0 ... 0.05} — what is data-awareness "
        "worth?"),
    (0, ""),
    (0, "5 fresh instances per point; means reported"),
], width=12.0)

# ---------- 11. Slack ----------
s = add_slide("Q1 — Slack: the scheduler matters exactly when it hurts",
              notes=(
    "At alpha = 1.0 the deadline barely fits. MILP leads at 1.38 "
    "against a bound of 1.43; rounding 1.25, greedy 1.23, GA 1.20. "
    "The ranking you see here is the paper's ranking under pressure. "
    "Loosen the deadline and the picture flips: greedy reaches the "
    "bound from alpha = 1.2, MILP by 1.5. But rounding and the GA "
    "never fully close the gap even at alpha = 2.0 — a fixed "
    "sampling budget does not recover the bound."))
pic(s, "perf_slack_accuracy.png", 0.7, 1.15, width=6.7)
bullets(s, [
    (0, "alpha = 1.0 (deadline barely fits): MILP 1.38 vs bound "
        "1.43; rounding 1.25, greedy 1.23, GA 1.20"),
    (0, "alpha >= 1.2: greedy reaches the bound; MILP joins by 1.5"),
    (0, "Rounding and GA trail 2.5-8% even at alpha = 2.0 — a fixed "
        "search budget cannot fully recover"),
    (0, "Lesson: method choice matters most exactly where the "
        "deadline binds"),
], left=7.7, width=5.1, top=1.3)

# ---------- 12. Federation size ----------
s = add_slide("Q2 — Federation size: capacity buys feasibility, not accuracy",
              notes=(
    "Grow the federation from 2 to 10 nodes. MILP and greedy sit "
    "exactly on the bound at every size. The GA drifts from about "
    "1.5% below the bound at N=2 to about 8% below at N=10; rounding "
    "matches only at N=2 and ends ~8% short. Why? Each node's "
    "chromosome/placement space grows, but the search budget is "
    "fixed. And notice — extra nodes never push anyone above the "
    "bound. They buy feasible placements, not accuracy."))
pic(s, "perf_nodes_accuracy.png", 0.7, 1.15, width=6.7)
bullets(s, [
    (0, "MILP and greedy match the bound at every N"),
    (0, "GA: ~1.5% below bound at N=2 -> ~8% below at N=10; rounding "
        "similar (~8% at N=10)"),
    (0, "Reason: placement space grows with N but the search budget "
        "is fixed"),
    (0, "Extra nodes never exceed the bound — they buy feasibility, "
        "not accuracy"),
], left=7.7, width=5.1, top=1.3)

# ---------- 13. Workflow size ----------
s = add_slide("Q3 — Workflow size: the simple greedy holds up best",
              notes=(
    "Now scale the workflow itself. At n=10 every method is on the "
    "bound — too small to separate them. At n=100 the GA is first "
    "to drift (1.26 vs bound ~1.40). At n=1000 the MILP exceeds our "
    "800-variable cap and drops out; rounding survives (1.37) but at "
    "roughly 93 seconds per LP re-solve, ~5-6 minutes per run; the "
    "GA falls to 1.10 in ~159 seconds. The greedy — milliseconds — "
    "stays on the bound. At 1000 tasks it is the only method that is "
    "both fast and optimal-accuracy."))
pic(s, "perf_task_size_accuracy.png", 0.7, 1.15, width=6.7)
bullets(s, [
    (0, "n = 10: all methods on the bound (1.41)"),
    (0, "n = 100: MILP + greedy on bound; GA first to drift (1.26)"),
    (0, "n = 1000: MILP past the 800-var cap; greedy on bound in "
        "0.15 s; rounding 1.37 (~93 s per LP re-solve, ~372 s/run); "
        "GA 1.10 in ~159 s"),
    (0, "GA budget is spread over a combinatorially growing space"),
], left=7.7, width=5.1, top=1.3)

# ---------- 14. Test-runs table ----------
s = add_slide("Same story on the four test datasets", notes=(
    "The per-dataset table agrees with the sweep. Small and medium: "
    "MILP, greedy — and at small scale also rounding and GA — hit "
    "the same score; greedy just does it in microseconds with the "
    "shortest makespan. Large and xlarge: only greedy and GA run; "
    "greedy keeps ~1.41 while the GA falls to 1.17 then 1.13 — and "
    "its makespan actually exceeds the greedy's by ~40%, spending "
    "73 seconds to lose."))
bullets(s, [
    (0, "small (10/3): all four methods identical score 1.64; "
        "greedy fastest and shortest makespan (16.8 vs ~18)"),
    (0, "medium (100/5): MILP + greedy 1.44; rounding 1.32; GA 1.27 "
        "— but greedy makespan 43.1 vs ~61"),
    (0, "large (500/8): only greedy + GA fit: 1.42 vs 1.17, "
        "makespan 50 vs 71"),
    (0, "xlarge (1000/10): greedy 1.41 in 0.14 s; GA 1.13 in 73 s "
        "with makespan 120"),
    (0, ""),
    (0, "Accuracy is not free in wall time — and neither is the "
        "makespan"),
], width=12.0)

# ---------- 15. Failures ----------
s = add_slide("Q4 — Failures: scores stay flat; feasibility is the story",
              notes=(
    "Here tasks fail independently and retry once in place — a retry "
    "doubles that task's runtime but keeps its accuracy if it still "
    "finishes. So scores barely move with the failure rate — look at "
    "feasibility instead. The greedy stays feasible at every rate; "
    "MILP and GA drop to ~60% by 0.5; rounding only ~20%. Why is "
    "greedy so robust? It already finishes early — makespan 27-35 "
    "vs the MILP's 38-79 — leaving slack for a retry to absorb."))
pic(s, "perf_failure_accuracy.png", 0.7, 1.15, width=6.7)
bullets(s, [
    (0, "Retry-once model: failed task reruns in place; accuracy "
        "kept if the retry meets the deadline"),
    (0, "Scores flat in failure rate — retries preserve accuracy"),
    (0, "Feasibility at rate 0.5: greedy 100%; MILP/GA ~60%; "
        "rounding ~20%"),
    (0, "Greedy's edge: it finishes early (makespan ~30 vs 40-80), "
        "leaving room for retries"),
], left=7.7, width=5.1, top=1.3)

# ---------- 16. Bandwidth ----------
s = add_slide("Q5 — Link degradation: what data-awareness is worth",
              notes=(
    "Finally, degrade every link — down to 5% of nominal bandwidth. "
    "The bandwidth-blind baseline is the cautionary tale: its scores "
    "look perfect, bound-level, at every degradation — because the "
    "score doesn't know the schedule is late. Feasibility tells the "
    "truth: 80% at 0.5x, 20% at 0.2x, zero below. Among data-aware "
    "methods: MILP stays feasible everywhere, losing ~10% score at "
    "0.05x; greedy holds feasibility to 0.1x but pays heavily in "
    "accuracy; the GA fails at 0.05x; rounding only survives above "
    "0.5x."))
pic(s, "perf_bandwidth_accuracy.png", 0.7, 1.15, width=6.7)
bullets(s, [
    (0, "Bandwidth-blind greedy: bound-level scores at every level — "
        "but infeasible (80% at 0.5x, 20% at 0.2x, 0% below)"),
    (0, "MILP: feasible at all levels; ~10% score loss at 0.05x"),
    (0, "Greedy: feasible to 0.1x, pays in accuracy (0.3-1.4 avg); "
        "collapses at 0.05x"),
    (0, "GA: holds to 0.1x, infeasible at 0.05x; rounding survives "
        "only above 0.5x"),
    (0, "High score + late = a missed alert, not a result"),
], left=7.7, width=5.1, top=1.3)

# ---------- 17. Big-graph scalability ----------
s = add_slide("Beyond the sweeps: 10^6-task structures", notes=(
    "Separately from scheduling, we stress-tested the generators "
    "themselves: DAGs up to a million tasks generate in ~3 seconds "
    "with stable shape — depth grows like log n, ~3 edges per node. "
    "Resource graphs up to a million fog nodes generate in ~7 "
    "seconds, degree ~5, bandwidth range stable. These are "
    "structural instances: scheduling a million-task dense instance "
    "is out of reach for the LP-based methods — the honest boundary "
    "is where constraints and memory hit the wall."))
bullets(s, [
    (0, "DAG generator: 10^6 tasks / ~3M edges in ~3 s; depth grows "
        "like log n (24 -> 91 for 100 -> 10^6)"),
    (0, "Resource graphs: 10^6 fog nodes in ~7 s; avg degree ~5, "
        "bandwidth 10-100"),
    (0, "Structural generation is cheap; schedulable dense instances "
        "stop where constraints do"),
    (1, "MILP: ~800 assignment vars; LP: ~10^5 rows at n=1000; "
        "dense n x n instancing ~10^4 tasks"),
], width=6.9)
pic(s, "resource_graphs.png", 7.6, 1.3, width=5.4, base=RES)
caption(s, "Generated federated resource graphs (up to 10^6 nodes)",
        7.6, 6.5, 5.4)

# =====================================================================
# ACT IV — WHAT IT MEANS
# =====================================================================

# ---------- 18. Takeaways ----------
s = add_slide("What we learned", notes=(
    "Four takeaways. One: the scheduler matters most exactly where "
    "the deadline binds — at loose slack almost anything works. "
    "Two: accuracy under a binding deadline is not free — it costs "
    "solver time; the greedy's 0.15 seconds buys bound-level "
    "accuracy at 1000 tasks where the LP methods cost minutes. "
    "Three: data-awareness is what keeps schedules feasible as links "
    "degrade — the blind baseline's perfect scores are just late "
    "schedules. Four: fixed search budgets don't scale — the GA's "
    "quality decays with both n and N."))
bullets(s, [
    (0, "1. The scheduler matters most exactly where the deadline "
        "binds — at loose slack almost anything works"),
    (0, "2. Accuracy under a binding deadline costs wall time: "
        "greedy 0.15 s vs rounding ~372 s vs GA ~159 s at n=1000"),
    (0, "3. Data-awareness buys feasibility, not score: the blind "
        "baseline's 'perfect' scores are late schedules"),
    (0, "4. Fixed search budgets decay — GA quality erodes with "
        "both n and N; size-adaptive budgets would close the gap"),
    (0, ""),
    (0, "Rule of thumb: MILP at moderate scale, greedy at large "
        "scale, rounding/GA only where their cost is affordable"),
], width=12.0)

# ---------- 19. Limitations ----------
s = add_slide("Honest limits", notes=(
    "What we do not claim. The MILP is capped at 800 assignment "
    "variables — beyond that it is the benchmark's boundary, not the "
    "result's. The LP grows ~10^5 rows at n=1000; our randomized "
    "rounding reduces trials as size grows, which is part of why its "
    "scores dip. The GA uses one fixed budget across all sizes. And "
    "the retry model is retry-once-in-place — no replication, no "
    "checkpointing, no migration to another node."))
bullets(s, [
    (0, "MILP capped at ~800 assignment variables — a deliberate "
        "boundary, not an oversight"),
    (0, "LP relaxation: ~10^5 constraint rows at n=1000; rounding "
        "trials reduced as size grows (part of its score dip)"),
    (0, "GA uses one fixed budget across all sizes — its gap is "
        "partly budget, partly search"),
    (0, "Failure model is retry-once-in-place — no replication, "
        "checkpointing, or cross-node migration yet"),
    (0, "Dense schedulable instances stop near 10^4 tasks; the 10^6 "
        "experiments are structural"),
], width=12.0)

# ---------- 20. Conclusion ----------
s = add_slide("Conclusion", notes=(
    "One joint formulation — placement, execution fraction, data "
    "movement — proved, linearized, and solver-ready. Four "
    "schedulers on one cost model, five sweeps, honest scalability "
    "limits. Next: decomposed formulations to reach the million-task "
    "regime for real, adaptive GA budgets, richer failure semantics, "
    "and an online re-scheduler on a real fog testbed. Everything "
    "reproduces — code, data, executed notebook — at the repo."))
bullets(s, [
    (0, "One joint formulation: task placement + execution fraction "
        "+ inter-node data movement, under a hard deadline"),
    (0, "Four schedulers sharing one cost model; five parameter "
        "sweeps; a verifiable benchmark at every scale"),
    (0, "MILP leads under pressure at moderate scale; the data-aware "
        "greedy is fast and bound-level at large scale"),
    (0, "Next: sparse/decomposed models toward 10^6 tasks, adaptive "
        "GA budgets, replication/checkpointing, online "
        "re-scheduling on a real testbed"),
    (0, ""),
    (0, "Reproduce it: github.com/gayanigupta/data-aware-scheduling "
        "— code, CSVs, executed notebook, this deck"),
], width=12.0)

# ---------- 21. Thank you ----------
s = add_slide(notes="Questions welcome.")
t = s.shapes.add_textbox(Inches(1), Inches(2.6), Inches(11.3), Inches(1.5))
p = t.text_frame.paragraphs[0]
p.text = "Thank you"
p.font.size = Pt(44); p.font.bold = True; p.font.color.rgb = NAVY
p.alignment = PP_ALIGN.CENTER
a = s.shapes.add_textbox(Inches(1), Inches(4.3), Inches(11.3), Inches(0.8))
p = a.text_frame.paragraphs[0]
p.text = "github.com/gayanigupta/data-aware-scheduling"
p.font.size = Pt(18); p.font.color.rgb = GREY
p.alignment = PP_ALIGN.CENTER


os.makedirs(os.path.dirname(OUT), exist_ok=True)
prs.save(OUT)
print("wrote", OUT, f"({len(prs.slides._sldIdLst)} slides)")
