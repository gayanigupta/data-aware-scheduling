"""Build the PhD proposal-defense slide deck.

Plain, black-and-white design: a title line at the top, plain
bulleted text, the paper's figures as visuals, and a slide
number.  No decorative colors or boxes -- it should look like
slides a person made in PowerPoint.

Structure:
  1. Motivation and setting
  2. Related work and the gap
  3. Problem definition
  4. Paper 1 (published, Cloud Summit 2025)
  5. Paper 2 (in revision, CCGrid 2027)
  6. Paper 3: the proposed research
  7. Evaluation plan, timeline, conclusion

Run from the repo root:  python3 code/make_slides.py
"""
import os

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "paper", "Figures")
RES = os.path.join(ROOT, "data", "results")
OUT = os.path.join(ROOT, "slides", "data-aware-scheduling.pptx")

INK  = RGBColor(0x1A, 0x1A, 0x1A)
GREY = RGBColor(0x59, 0x59, 0x59)
FAINT = RGBColor(0xE8, 0xE8, 0xE8)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

PAGE_W = Inches(13.333)
PAGE_H = Inches(7.5)

prs = Presentation()
prs.slide_width = PAGE_W
prs.slide_height = PAGE_H
BLANK = prs.slide_layouts[6]
_no = 0


def _num(slide):
    global _no
    _no += 1
    tb = slide.shapes.add_textbox(Inches(12.5), Inches(7.1),
                                  Inches(0.7), Inches(0.3))
    p = tb.text_frame.paragraphs[0]
    p.text = str(_no)
    p.font.size = Pt(10)
    p.font.color.rgb = GREY
    p.alignment = PP_ALIGN.RIGHT


def slide(title=None, notes=None):
    """Plain white slide: bold title top-left, thin rule, number."""
    s = prs.slides.add_slide(BLANK)
    if title:
        tb = s.shapes.add_textbox(Inches(0.5), Inches(0.25),
                                  Inches(12.4), Inches(0.75))
        tb.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tb.text_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(30)
        p.font.bold = True
        p.font.color.rgb = INK
        ln = s.shapes.add_connector(1, Inches(0.55), Inches(1.05),
                                    Inches(12.8), Inches(1.05))
        ln.line.color.rgb = INK
        ln.line.width = Pt(1.0)
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    _num(s)
    return s


def bullets(s, items, left=0.7, top=1.35, width=12.0, height=5.5,
            size=20):
    """'items' = list of (level, text). Real bullet glyphs."""
    tb = s.shapes.add_textbox(Inches(left), Inches(top),
                              Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    first = True
    for level, text in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        if not text:
            p.text = ""
            p.space_after = Pt(4)
            continue
        p.text = ("\u2022  " if level == 0 else "      \u2013 ") + text
        p.font.size = Pt(size if level == 0 else size - 2)
        p.font.color.rgb = INK if level == 0 else GREY
        p.space_after = Pt(10)
    return tb


def para(s, text, left=0.7, top=1.35, width=12.0, size=20,
         bold=False, color=INK, italic=False):
    tb = s.shapes.add_textbox(Inches(left), Inches(top),
                              Inches(width), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.italic = italic
    p.font.color.rgb = color
    return tb


def takeaway(s, text, top=6.15):
    """A plain bold line under a hairline rule."""
    ln = s.shapes.add_connector(1, Inches(0.7), Inches(top),
                                Inches(12.6), Inches(top))
    ln.line.color.rgb = GREY
    ln.line.width = Pt(0.75)
    tb = s.shapes.add_textbox(Inches(0.7), Inches(top + 0.1),
                              Inches(11.9), Inches(1.0))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Take-away:  " + text
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = INK


def pic(s, path, left, top, width=None, height=None, base=FIG):
    kw = {}
    if width:
        kw["width"] = Inches(width)
    if height:
        kw["height"] = Inches(height)
    s.shapes.add_picture(os.path.join(base, path),
                         Inches(left), Inches(top), **kw)


def caption(s, text, left, top, width):
    tb = s.shapes.add_textbox(Inches(left), Inches(top),
                              Inches(width), Inches(0.5))
    p = tb.text_frame.paragraphs[0]
    p.text = text
    p.font.size = Pt(13)
    p.font.italic = True
    p.font.color.rgb = GREY
    p.alignment = PP_ALIGN.CENTER


def table(s, rows, l, t, w, h, col_widths=None, size=14):
    """Plain table: black header row, white body."""
    nr, nc = len(rows), len(rows[0])
    gfx = s.shapes.add_table(nr, nc, Inches(l), Inches(t),
                             Inches(w), Inches(h))
    tbl = gfx.table
    if col_widths:
        for i, cw in enumerate(col_widths):
            tbl.columns[i].width = Inches(cw)
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = tbl.cell(ri, ci)
            cell.fill.solid()
            cell.fill.fore_color.rgb = FAINT if ri == 0 else WHITE
            cell.margin_top = Pt(4); cell.margin_bottom = Pt(4)
            cell.margin_left = Pt(8); cell.margin_right = Pt(8)
            p = cell.text_frame.paragraphs[0]
            cell.text_frame.word_wrap = True
            p.text = str(val)
            p.font.size = Pt(size)
            p.font.bold = ri == 0
            p.font.color.rgb = INK
    return tbl


def section(title, sub, notes=None):
    """Minimal section slide: centered text on white."""
    s = prs.slides.add_slide(BLANK)
    tb = s.shapes.add_textbox(Inches(1), Inches(2.6),
                              Inches(11.3), Inches(1.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(38)
    p.font.bold = True
    p.font.color.rgb = INK
    p.alignment = PP_ALIGN.CENTER
    sb = s.shapes.add_textbox(Inches(1), Inches(4.0),
                              Inches(11.3), Inches(1.2))
    tf = sb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = sub
    p.font.size = Pt(20)
    p.font.color.rgb = GREY
    p.alignment = PP_ALIGN.CENTER
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    _num(s)
    return s


# ==================================================================
# Title
# ==================================================================
s = prs.slides.add_slide(BLANK)
_no += 1
tb = s.shapes.add_textbox(Inches(0.8), Inches(1.7), Inches(11.7),
                          Inches(2.6))
tf = tb.text_frame
tf.word_wrap = True
for i, (txt, sz, bold) in enumerate([
        ("Dynamic Partial Repartitioning of DAG Workflows", 34, True),
        ("after Resource Failures in Federated Fog "
         "Environments", 34, True),
        ("", 14, False),
        ("PhD Research Proposal", 20, False)]):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = txt
    p.font.size = Pt(sz)
    p.font.bold = bold
    p.font.color.rgb = INK
    p.alignment = PP_ALIGN.CENTER
ln = s.shapes.add_connector(1, Inches(4.2), Inches(4.6),
                            Inches(9.1), Inches(4.6))
ln.line.color.rgb = INK
ln.line.width = Pt(1.0)
sb = s.shapes.add_textbox(Inches(0.8), Inches(4.9), Inches(11.7),
                          Inches(2.2))
tf = sb.text_frame
tf.word_wrap = True
for i, txt in enumerate([
        "Gayani Gupta",
        "Department of Computer Science and Engineering, "
        "University of North Texas",
        "Advisors: Dr. Mohsen Amini Salehi and "
        "Dr. Sanjukta Bhowmick"]):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = txt
    p.font.size = Pt(18 if i == 0 else 16)
    p.font.color.rgb = INK if i == 0 else GREY
    p.alignment = PP_ALIGN.CENTER
s.notes_slide.notes_text_frame.text = (
    "Good morning. This is my PhD proposal. The talk has three "
    "parts: the problem and why it matters, the two papers that "
    "are already done, and the third piece of research I am "
    "proposing.")

# ==================================================================
# Outline
# ==================================================================
s = slide("What this talk covers", notes=(
    "Quick outline. The first half sets up the problem and the "
    "related work. The second half is the completed work and "
    "the proposal."))
bullets(s, [
    (0, "The setting and why it matters"),
    (0, "What is already known, and the gap"),
    (0, "The problem, stated precisely"),
    (0, "Paper 1 \u2013 task allocation across federated fog "
        "(published, IEEE Cloud Summit 2025)"),
    (0, "Paper 2 \u2013 data-aware scheduling with approximation "
        "(in revision, CCGrid 2027)"),
    (0, "Paper 3 \u2013 what I am proposing: partial "
        "repartitioning after a resource fails"),
    (0, "How I will evaluate it, the timeline, and what it "
        "contributes"),
], top=1.4)

# ==================================================================
# Motivation
# ==================================================================
section("The setting", "Why this problem exists",
        notes="First, the setting. The scenario is a disaster "
              "response workflow that has to run exactly when "
              "the network is at its worst.")

s = slide("A disaster-response workflow", notes=(
    "Picture a river basin starting to flood. The response "
    "workflow runs as a chain of dependent tasks: sensors "
    "feed models, models feed forecasts, forecasts drive "
    "plans and alerts. The deadline is not a preference. A "
    "forecast that arrives after the water has risen is a "
    "forecast nobody uses. And the same event that creates "
    "the deadline is often the thing that takes the cloud "
    "link down."))
bullets(s, [
    (0, "A flood, a wildfire, an offshore platform incident \u2014 "
        "a workflow that has to finish on time"),
    (0, "The deadline is hard: a late forecast is a missed "
        "alert, not a result"),
    (0, "The same event that creates the deadline often takes "
        "the cloud link down with it"),
])

s = slide("The federated fog is what is left", notes=(
    "What remains is the fog: cell-tower racks, roadside "
    "cabinets, platform servers near the event. No single "
    "site is strong enough alone, but they keep fast links "
    "to each other even when the uplink dies. Federating "
    "them creates a small local cloud. The price is that "
    "every task now has a choice of where to run, and every "
    "choice moves data across a link."))
bullets(s, [
    (0, "Nearby fog sites keep fast, stable links to each "
        "other even when the cloud uplink is gone"),
    (0, "One site is rarely enough for the whole workflow; "
        "federating them creates a small local cloud"),
    (0, "But now every task can run in many places, and "
        "wherever it runs, its input has to travel there "
        "first"),
], width=6.6)
pic(s, "federated-fog-architecture.png", 7.5, 1.3, width=5.4)
caption(s, "Fog sites federated around a disaster area",
        7.5, 6.5, 5.4)

s = slide("Two things make the scheduling hard", notes=(
    "Two difficulties. First, data movement: every edge in "
    "the workflow carries data, and a slow link can make a "
    "transfer cost as much as the task itself \u2014 so the "
    "fastest machine can turn out to be the worst choice. "
    "Second, accuracy is tradeable: most of these tasks can "
    "run partially. A flood model at eighty percent fidelity "
    "still warns people in time. And the two interact, "
    "because placement decides the transfers while the "
    "fractions decide the runtimes."))
bullets(s, [
    (0, "Data movement rivals computation"),
    (1, "every dependency edge carries data across a link, "
        "and the transfer can take as long as the task "
        "itself"),
    (0, "Accuracy is a tradeable resource"),
    (1, "a task can run partially \u2014 half the work, half "
        "the time, half the accuracy \u2014 and often that "
        "is enough"),
    (0, "And the two interact: where a task runs decides "
        "its transfer costs, while how much of it runs "
        "decides its runtime"),
])

s = slide("The PhD as three papers", notes=(
    "The dissertation is one story told in three papers. The "
    "first, published at Cloud Summit last year, built the "
    "model and four schedulers for it. The second hardened "
    "it: it made the model data-aware, added an accuracy "
    "bound to score against, and stress-tested the whole "
    "thing. The third, which is what I am proposing today, "
    "asks what happens when a resource fails in the middle "
    "of a run. Each paper answers the question the previous "
    "one left open."))
bullets(s, [
    (0, "Paper 1 \u2013 the model and four schedulers for "
        "allocating DAG workflows across federated fog"),
    (1, "published at IEEE Cloud Summit 2025"),
    (0, "Paper 2 \u2013 makes the model data-aware: an "
        "accuracy bound, retry semantics, bandwidth "
        "degradation, scalability limits"),
    (1, "manuscript in revision for CCGrid 2027"),
    (0, "Paper 3 \u2013 dynamic partial repartitioning when "
        "a resource fails mid-workflow"),
    (1, "this proposal; the target is IPDPS or CCGrid 2028"),
], top=1.5)

# ==================================================================
# Related work
# ==================================================================
section("What is already known", "Four research threads, and "
        "the gap none of them covers",
        notes="Now the related work. Four threads matter here, "
              "and I will end on the gap.")

s = slide("Classic DAG scheduling", notes=(
    "The reference point is HEFT: rank the tasks by their "
    "upward rank and place each one where it will finish "
    "earliest. It is a very good algorithm, and the family "
    "around it \u2014 CPOP, PEFT, the cloud workflow work of "
    "Abrishami and of Yu and Buyya \u2014 refines the same "
    "idea. But all of them share three assumptions that do "
    "not hold here: tasks always run completely, transfers "
    "are just static edge weights, and the plan is fixed "
    "before execution starts."))
bullets(s, [
    (0, "HEFT (Topcuoglu et al., 2002) is the reference "
        "algorithm: rank the tasks, place each one where it "
        "finishes earliest"),
    (0, "CPOP, PEFT, and the cloud workflow schedulers "
        "(Abrishami; Yu and Buyya) refine the same idea"),
    (0, "But all of them assume tasks run completely, "
        "transfers are static edge weights, and the plan is "
        "fixed before execution"),
    (0, "Our first paper sits in this line: it adds "
        "federation and eligibility to the classic model"),
])

s = slide("Fog and edge scheduling", notes=(
    "The fog scheduling literature handles the things that "
    "make fog hard: small capacities, heterogeneous "
    "machines, eligibility. Surveys like Mouradian's "
    "catalog the placement policies. What the literature "
    "mostly does not do is price the links \u2014 locality "
    "is acknowledged, but per-link bandwidth is rarely a "
    "first-class cost. And tasks are still treated as "
    "atomic."))
bullets(s, [
    (0, "Fog schedulers handle capacity, eligibility, and "
        "heterogeneity across edge, fog, and cloud tiers"),
    (0, "Locality is acknowledged, but per-link bandwidth "
        "is rarely priced as a first-class cost"),
    (0, "Tasks are atomic: they run completely or not at "
        "all"),
    (0, "And failures are handled by restarting, not by "
        "repairing"),
])

s = slide("Approximate computing, and failure recovery", notes=(
    "Two shorter threads. Approximate computing trades "
    "quality for time \u2014 exactly what a tight deadline "
    "needs \u2014 but it assumes the data is already where "
    "it needs to be. On failures: rescheduling work like "
    "Sakellariou and Zhao reconsiders a workflow at chosen "
    "points but remaps the whole thing; checkpointing and "
    "replication recover the work at a real cost; and there "
    "is a whole graph literature on updating shortest paths "
    "incrementally after a graph change. None of it couples "
    "a node failure to the affected region of the task "
    "graph."))
bullets(s, [
    (0, "Approximate computing trades quality for time \u2014 "
        "useful under deadlines"),
    (1, "but it assumes the data is already where it needs "
        "to be; the transfer cost is not part of the "
        "trade"),
    (0, "Workflow rescheduling remaps the whole DAG at "
        "chosen points (Sakellariou and Zhao, 2004)"),
    (0, "Checkpointing and replication recover the work, "
        "at a real recompute or replication cost"),
    (0, "Dynamic shortest-path updates repair routing "
        "after a graph change \u2014 nobody has used them "
        "for workflow repartitioning"),
])

s = slide("The gap", notes=(
    "This table summarizes it. Read each column as a "
    "capability. Classic schedulers place tasks but price "
    "nothing about data. Fog schedulers add some data "
    "awareness. Our completed work adds approximate "
    "execution. And the last column \u2014 repairing only "
    "the affected region when a resource fails \u2014 is "
    "empty. That empty column is the proposal."))
table(s, [
    ["Capability", "Classic (HEFT)", "Fog schedulers",
     "Papers 1+2", "This proposal"],
    ["Heterogeneous placement", "yes", "yes", "yes", "yes"],
    ["Data transfers priced per link", "no", "partial",
     "yes", "yes"],
    ["Approximate execution", "no", "no", "yes", "yes"],
    ["Recovery after a failure", "restart", "reschedule all",
     "retry the task", "repair only the region"],
], 0.8, 1.5, 11.7, 3.6,
    col_widths=[4.0, 1.9, 1.9, 1.9, 2.0], size=14)
para(s, "Nobody couples a resource failure to the smallest "
        "affected region of the workflow graph.",
     top=5.6, size=19, bold=True)

# ==================================================================
# Problem definition
# ==================================================================
section("The problem, stated precisely",
        "Two graphs, one coupling, a hard deadline",
        notes="Before the algorithms, let me pin the problem "
              "down \u2014 both the static version the "
              "completed work solved and the dynamic version "
              "this proposal adds.")

s = slide("The model: two graphs", notes=(
    "Two graphs. The task graph holds the work: each task "
    "has an execution time, an accuracy it returns when run "
    "fully, and a list of machines it is allowed to use. "
    "Every edge carries dependency data. The infrastructure "
    "graph holds the machines: capacity, memory, "
    "availability, and the bandwidths between them. A "
    "schedule maps one graph onto the other. A failure "
    "deletes a node from one graph and strands work in the "
    "other."))
bullets(s, [
    (0, "The task graph holds the work:"),
    (1, "each task has an execution time, a full-run "
        "accuracy, and the machines it is allowed to use"),
    (1, "every edge carries a chunk of dependency data"),
    (0, "The infrastructure graph holds the machines:"),
    (1, "capacity, memory, availability, and the bandwidth "
        "between every pair"),
    (0, "A schedule maps tasks onto machines; a failure "
        "deletes a machine and strands whatever was on it"),
])

s = slide("The static problem (Papers 1 and 2)", notes=(
    "The completed work solved this version. Given the two "
    "graphs and a deadline: decide where each task runs and "
    "how much of it runs, so that every task waits for its "
    "data and everything finishes on time \u2014 and "
    "maximize the average accuracy. It is NP-hard, so the "
    "exact solver is the benchmark, not the product."))
bullets(s, [
    (0, "Given: the task graph, the infrastructure graph, "
        "and a deadline"),
    (0, "Decide: for every task, which eligible machine it "
        "runs on, and how much of it runs"),
    (0, "So that: a task starts only after its "
        "predecessors finish and their data arrives, and "
        "everything is done by the deadline"),
    (0, "Maximize: the average accuracy"),
    (0, ""),
    (0, "The problem is NP-hard even on parallel machines, "
        "so the exact solver is a reference, not the "
        "product"),
], top=1.5)

s = slide("The dynamic problem (Paper 3)", notes=(
    "The proposal adds one event to the same model. Partway "
    "through execution, a machine fails. Whatever was "
    "unfinished on it is stranded. The question is no "
    "longer where to put everything \u2014 it is which part "
    "of the workflow actually needs repair, and where the "
    "stranded work should go, disturbing as little as "
    "possible. Done work is never redone. Healthy "
    "placements never move."))
bullets(s, [
    (0, "Event: partway through the run, a machine fails; "
        "its unfinished tasks are stranded"),
    (0, "Decide: which part of the workflow has to be "
        "repaired, and where its tasks go on the surviving "
        "machines"),
    (0, "So that: completed work never restarts, healthy "
        "placements never move, and the deadline still "
        "holds"),
    (0, "Minimize: the recovery cost \u2014 added runtime, "
        "tasks moved, data re-shipped \u2014 while keeping "
        "the accuracy"),
], top=1.5)

# ==================================================================
# Paper 1
# ==================================================================
section("Paper 1", "Task allocation across federated fog \u2014 "
        "published at IEEE Cloud Summit 2025",
        notes="Now the completed work. Paper one established "
              "the model and four ways to solve it.")

s = slide("What Paper 1 did", notes=(
    "Paper one made three contributions. It formulated the "
    "problem as a mixed-integer program with correctness "
    "proofs. It built three scalable schedulers around the "
    "same cost model \u2014 a rounding scheme, a greedy, "
    "and a genetic algorithm \u2014 so the differences "
    "between them are algorithmic rather than accounting "
    "differences. And it showed the formulation holds "
    "together on real instances."))
bullets(s, [
    (0, "Formulated the joint problem \u2014 where each "
        "task runs and how much of it runs \u2014 as a "
        "mixed-integer program"),
    (0, "Proved the formulation correct: a unique "
        "assignment, respected precedence, a held "
        "deadline, and an optimum that is the "
        "maximum-accuracy feasible schedule"),
    (0, "Built three scalable schedulers on the same cost "
        "model: LP rounding, a data-aware greedy, and a "
        "genetic algorithm"),
    (0, "Published at IEEE Cloud Summit 2025"),
    (0, ""),
    (0, "What it left open: no bound to score against, no "
        "link-degradation study, no machine-level "
        "failures"),
])

# ==================================================================
# Paper 2
# ==================================================================
section("Paper 2", "Data-aware scheduling of approximate DAG "
        "workflows \u2014 in revision for CCGrid 2027",
        notes="Paper two hardened the model. I will show the "
              "schedulers, the experimental setup, and then "
              "the five experiments, each with its "
              "take-away.")

s = slide("What Paper 2 added", notes=(
    "Paper two added four things on top of paper one. A "
    "max-accuracy bound so a score finally means "
    "something. A bandwidth-blind baseline to show what "
    "data-awareness is worth. A retry-once failure model. "
    "And an honest account of where each method breaks."))
bullets(s, [
    (0, "A max-accuracy bound, so a reported score finally "
        "means something"),
    (0, "A bandwidth-blind baseline \u2014 a scheduler that "
        "ignores the links \u2014 to measure what "
        "data-awareness buys"),
    (0, "A retry-once failure model at task level"),
    (0, "An honest account of where each method breaks: "
        "solver caps, search budgets, dense-storage "
        "limits"),
])

s = slide("Four schedulers, one cost model", notes=(
    "Every method prices transfers the same way, so "
    "differences are algorithmic. The MILP is the "
    "reference. LP rounding relaxes the integer choices, "
    "samples a machine per task, and re-solves the "
    "fractions. The greedy places ready tasks by earliest "
    "finish and retries with a smaller fraction when the "
    "deadline is missed. The genetic algorithm searches "
    "assignments and fractions together."))
pic(s, "scheduling-pipeline.png", 0.7, 1.3, width=6.6)
bullets(s, [
    (0, "The exact solver is the benchmark"),
    (0, "LP rounding relaxes, samples a machine per task, "
        "re-solves the fractions"),
    (0, "The greedy places ready tasks by earliest finish; "
        "on a deadline miss it lowers the fraction and "
        "retries"),
    (0, "The GA searches assignments and fractions as one "
        "chromosome"),
], left=7.7, width=5.2, top=1.5, size=17)

s = slide("Experimental setup", notes=(
    "The setup before the results. A discrete-event "
    "simulator in NumPy with the HiGHS solver. The "
    "parameters are chosen so a transfer can genuinely "
    "rival a task, which is the regime that matters. Four "
    "datasets, five sweeps, five fresh instances per "
    "point."))
table(s, [
    ["Component", "Setting"],
    ["Simulator", "discrete-event, Python/NumPy + SciPy HiGHS"],
    ["Task runtimes", "uniform 1\u20135"],
    ["Data per edge", "uniform 5\u201350"],
    ["Link bandwidths", "uniform 10\u2013100 (a transfer can "
     "rival a task)"],
    ["Workflow sizes", "10, 100, 500, 1000 tasks on 3\u201310 "
     "machines"],
    ["Sweeps", "deadline slack, federation size, workflow "
     "size, failure rate, bandwidth"],
    ["Metrics", "score vs. the bound, feasibility, wall time "
     "(5 fresh instances per point)"],
], 0.9, 1.4, 11.5, 5.0, col_widths=[3.2, 8.3], size=14)

s = slide("Deadline slack", notes=(
    "First experiment: tighten the deadline. When it barely "
    "fits, the exact solver leads and everything else "
    "trails. Give it a little room and the greedy reaches "
    "the bound. So the method choice matters exactly where "
    "the deadline binds."))
pic(s, "perf_slack_accuracy.png", 0.7, 1.2, width=6.7)
bullets(s, [
    (0, "When the deadline barely fits, the exact solver "
        "leads (1.38 vs. a bound of 1.43); the others "
        "trail"),
    (0, "A little slack and the greedy reaches the bound"),
    (0, "Rounding and the GA stay 2.5\u20138% below even "
        "with slack to spare"),
], left=7.8, width=5.0, top=1.5, size=16)
takeaway(s, "the method choice matters exactly where the "
         "deadline binds; with loose slack almost anything "
         "works")

s = slide("Federation size", notes=(
    "Scale the federation from two to ten machines. The "
    "exact solver and the greedy sit on the bound "
    "throughout. The GA and rounding drift further below "
    "as the placement space grows while their search "
    "budget stays fixed."))
pic(s, "perf_nodes_accuracy.png", 0.7, 1.2, width=6.7)
bullets(s, [
    (0, "The exact solver and the greedy match the bound "
        "at every size"),
    (0, "The GA drifts from 1.5% below the bound at two "
        "machines to about 8% at ten"),
    (0, "A bigger placement space with a fixed search "
        "budget just means a worse search"),
], left=7.8, width=5.0, top=1.5, size=16)
takeaway(s, "more machines buy feasibility, not accuracy "
         "\u2014 extra capacity never lifts a method above "
         "the bound")

s = slide("Workflow size", notes=(
    "Scale the workflow instead. At ten tasks everyone is "
    "on the bound. At a thousand, only the greedy is still "
    "there \u2014 in a fifth of a second. Rounding "
    "survives but pays about ninety seconds per re-solve, "
    "and the GA falls while taking over two minutes."))
pic(s, "perf_task_size_accuracy.png", 0.7, 1.2, width=6.7)
bullets(s, [
    (0, "At 10 tasks all four methods sit on the bound"),
    (0, "At 1000 tasks the exact solver is past its cap; "
        "the greedy stays on the bound in 0.15 s"),
    (0, "Rounding needs ~93 s per re-solve; the GA drops "
        "to 1.10 in ~159 s"),
], left=7.8, width=5.0, top=1.5, size=16)
takeaway(s, "at scale only the greedy is both fast and "
         "bound-level")

s = slide("Task failures", notes=(
    "The failure model is retry-once: a failed task reruns "
    "in place and keeps its accuracy if the retry still "
    "meets the deadline. Scores stay flat for everyone; "
    "feasibility is where the methods separate. The greedy "
    "stays feasible at every rate because it finishes "
    "early and leaves room for the retry."))
pic(s, "perf_failure_accuracy.png", 0.7, 1.2, width=6.7)
bullets(s, [
    (0, "Retry-once: a failed task reruns in place, and "
        "keeps its accuracy if the retry still meets the "
        "deadline"),
    (0, "Scores stay flat for everyone; feasibility is "
        "where they separate"),
    (0, "At the highest failure rate: greedy still 100% "
        "feasible, the others drop to ~60% and ~20%"),
], left=7.8, width=5.0, top=1.5, size=16)
takeaway(s, "under failures the differentiator is "
         "feasibility \u2014 finishing early is what "
         "absorbs the retries")

s = slide("Link degradation", notes=(
    "This is the experiment the model was built for. "
    "Degrade every link down to five percent of nominal. "
    "The blind baseline reports bound-level scores at "
    "every level \u2014 on schedules that are infeasible. "
    "The data-aware methods trade accuracy for "
    "feasibility and degrade gracefully."))
pic(s, "perf_bandwidth_accuracy.png", 0.7, 1.2, width=6.7)
bullets(s, [
    (0, "The bandwidth-blind baseline shows bound-level "
        "scores at every level \u2014 while going fully "
        "infeasible below a fifth of nominal"),
    (0, "The exact solver stays feasible throughout and "
        "loses only ~10% of score"),
    (0, "The greedy stays feasible to a tenth by paying "
        "in accuracy"),
], left=7.8, width=5.0, top=1.5, size=16)
takeaway(s, "a scheduler that ignores the links reports a "
         "perfect score on a workflow that finishes late")

s = slide("The same story at every scale", notes=(
    "The per-dataset table says the same thing. On small "
    "instances everyone ties. On medium, the greedy's "
    "makespan is 43 versus about 61 for the rest. At the "
    "large sizes only the greedy and the GA even fit in "
    "memory, and the greedy holds the bound while the GA "
    "pays tens of seconds."))
table(s, [
    ["Dataset", "Method", "Score", "Makespan", "Runtime"],
    ["small (10 tasks)", "all four", "1.64", "17\u201319",
     "< 0.3 s"],
    ["medium (100)", "exact / greedy", "1.44", "61 / 43",
     "1.4 s / 0.003 s"],
    ["medium (100)", "rounding / GA", "1.32 / 1.27",
     "62 / 61", "25 s / 5.2 s"],
    ["large (500)", "greedy / GA", "1.42 / 1.17", "50 / 71",
     "0.04 s / 21 s"],
    ["xlarge (1000)", "greedy / GA", "1.41 / 1.13", "83 / 120",
     "0.14 s / 73 s"],
], 0.9, 1.4, 11.5, 3.8,
    col_widths=[3.0, 2.6, 1.7, 2.2, 2.0], size=14)
takeaway(s, "accuracy is not free in wall time, and neither "
         "is the makespan \u2014 the gap widens with scale")

s = slide("Honest limits, and what they leave open", notes=(
    "What we do not claim. The exact solver caps near 800 "
    "assignment variables. The LP reaches a hundred "
    "thousand rows at a thousand tasks. The GA runs on one "
    "fixed budget. And the failure model is "
    "retry-once-in-place \u2014 no replication, no "
    "checkpointing, no migration. That last limit is the "
    "bridge to the proposal."))
bullets(s, [
    (0, "The exact solver is capped near 800 assignment "
        "variables \u2014 a deliberate boundary"),
    (0, "The relaxation reaches ~100,000 rows at 1,000 "
        "tasks; the GA runs on one fixed budget"),
    (0, "The failure model is retry-once-in-place: no "
        "replication, checkpointing, or migration"),
    (0, "Schedulable instances stop near 10\u00b9\u2074 "
        "tasks; the million-task experiments are "
        "structural"),
    (0, ""),
    (0, "What is open: a whole machine fails mid-run, and "
        "the schedule was decided up front"),
])

# ==================================================================
# Paper 3 — proposed research
# ==================================================================
section("Paper 3 \u2014 the proposal",
        "Dynamic partial repartitioning after a resource "
        "failure",
        notes="Now the proposal itself. The question, the "
              "three research questions inside it, and the "
              "method.")

s = slide("The question", notes=(
    "The proposal in one sentence. When a fog machine "
    "fails mid-workflow, I want to repartition and "
    "reschedule only the affected part \u2014 not the "
    "whole workflow \u2014 while keeping the recovery "
    "time, the moved tasks, and the re-shipped data small. "
    "Three research questions decompose it."))
para(s, "How can we repartition and reschedule only the "
        "affected part of a DAG workflow after a fog "
        "resource fails \u2014 while keeping recovery time, "
        "task movement, data re-shipped, and completion "
        "time small?",
     top=1.4, width=12.0, size=21, bold=True)
bullets(s, [
    (0, "RQ1 \u2013 the boundary: what is the smallest part "
        "of the workflow that must be repartitioned?"),
    (0, "RQ2 \u2013 the repair: how do we repartition it "
        "onto surviving machines at minimum cost and still "
        "meet the deadline?"),
    (0, "RQ3 \u2013 the paths: how do we update "
        "communication paths incrementally instead of "
        "recomputing them?"),
], top=3.5)

s = slide("What a failure looks like mid-run", notes=(
    "Monitoring detects the failed machine. Its unfinished "
    "tasks are stranded and have to be rescued; completed "
    "work is never redone. The subtle decision is the "
    "boundary: sometimes a task that ran fine still has to "
    "move, because its input now sits across a slow path, "
    "or because staying pushes it past the deadline."))
bullets(s, [
    (0, "A machine dies with work still queued or running "
        "on it"),
    (0, "The stranded tasks must move \u2014 that part is "
        "mandatory"),
    (0, "But some neighbors may have to move too:"),
    (1, "a task whose input now crosses a path too slow "
        "to serve it in time"),
    (1, "a task that can no longer finish by the deadline "
        "if it stays"),
    (0, "The invariant throughout: completed work never "
        "restarts, and tasks that are fine never move"),
], top=1.5)

s = slide("The method, in seven steps", notes=(
    "Seven steps. The existing schedulers make the "
    "initial partition \u2014 that is paper one. When a "
    "failure is detected we isolate the stranded tasks, "
    "grow the smallest affected region under the boundary "
    "rule, pick replacements by capacity and distance to "
    "the parents and children, repartition just that "
    "region under a recovery cost model, update only the "
    "affected communication paths, and resume from the "
    "last good point."))
bullets(s, [
    (0, "1.  Make the initial partition (any paper-1 "
        "scheduler)"),
    (0, "2.  Detect the failure"),
    (0, "3.  Isolate the affected region \u2014 stranded "
        "tasks plus neighbors that fail a stay-test"),
    (0, "4.  Pick replacement machines by capacity and "
        "distance to where the parents and children "
        "live"),
    (0, "5.  Repartition only that region under the "
        "recovery cost model"),
    (0, "6.  Update only the affected communication "
        "paths"),
    (0, "7.  Resume from the last good point"),
], top=1.5)

s = slide("RQ1: where does the boundary lie?", notes=(
    "The technical heart of the proposal. The stranded set "
    "is mandatory. Beyond that we grow the region while a "
    "neighbor fails one of two stay-tests: it cannot make "
    "the deadline if it stays, or its input can no longer "
    "reach it in time. We stop when nothing fails a test, "
    "or at a size cap. Minimality of that region is the "
    "claim we verify \u2014 I expect it to grow with "
    "failure location and remaining slack."))
bullets(s, [
    (0, "Start with the stranded tasks \u2014 mandatory"),
    (0, "Then admit a neighbor only while it fails a "
        "stay-test:"),
    (1, "deadline test \u2013 staying pushes its finish "
        "time past the remaining slack"),
    (1, "locality test \u2013 staying strands its input "
        "on a path too slow to serve it in time"),
    (0, "Stop when no neighbor fails, or at a size cap"),
    (0, "The tasks that stayed put become fixed anchors "
        "the repair must respect"),
], top=1.5)

s = slide("RQ2: repairing the region", notes=(
    "The repair is a smaller instance of the same "
    "optimization family \u2014 which is the point: the "
    "paper-two schedulers become the region solvers. The "
    "recovery objective adds movement terms to the "
    "accuracy objective: added makespan, tasks moved, "
    "bytes re-shipped. The boundary anchors enter as "
    "fixed arrival times the repair must respect. A "
    "greedy repair answers in milliseconds; the exact "
    "solver is the reference on small regions."))
bullets(s, [
    (0, "Repair is a smaller instance of the same "
        "optimization \u2014 the paper-2 schedulers become "
        "the region solvers"),
    (0, "The objective minimizes added makespan plus "
        "tasks moved plus data re-shipped, subject to "
        "accuracy and the deadline"),
    (0, "The anchors enter as constants: arrival times "
        "of data from tasks that stayed put"),
    (0, "A greedy repair gives millisecond answers; the "
        "exact solver is the reference on small regions"),
], top=1.5)

s = slide("RQ3: updating the paths", notes=(
    "Moved tasks need new communication paths to their "
    "parents and children. Recomputing all shortest paths "
    "mid-workflow is too slow, so we reuse dynamic "
    "shortest-path updates \u2014 the work of Riazi, "
    "Khanda, and Dr. Bhowmick's group. Only the paths "
    "through the deleted machine and the moved tasks get "
    "updated. Using them to drive workflow recovery is, "
    "as far as we know, new."))
bullets(s, [
    (0, "Moved tasks need new paths to their parents and "
        "children"),
    (0, "Recomputing all shortest paths mid-workflow is "
        "too slow"),
    (0, "So we reuse dynamic shortest-path updates "
        "(Riazi, Khanda, Bhowmick and colleagues):"),
    (1, "only paths through the deleted machine and the "
        "moved tasks change"),
    (0, "Using dynamic path updates to drive workflow "
        "recovery is, as far as we know, new"),
], top=1.5)

s = slide("What is new here", notes=(
    "The pieces exist separately: dynamic path updates, "
    "fog rescheduling, partial reconsideration. Nobody "
    "couples them. The novelty is the mapping: a failure "
    "in the machine graph becomes the smallest affected "
    "region in the task graph."))
bullets(s, [
    (0, "Dynamic shortest-path updates exist \u2014 but "
        "have never driven workflow repartitioning"),
    (0, "Fog rescheduling exists \u2014 but without the "
        "two-graph coupling"),
    (0, "Partial workflow reconsideration exists \u2014 "
        "but not at failure granularity"),
    (0, ""),
    (0, "What is new: a machine failure maps to the "
        "smallest affected region; only that region is "
        "repartitioned; only its paths update; the "
        "workflow resumes"),
], top=1.5)

# ==================================================================
# Evaluation plan & timeline
# ==================================================================
section("Evaluation plan and timeline",
        "Baselines, metrics, hypotheses, milestones",
        notes="How I will test it, and when.")

s = slide("Baselines and metrics", notes=(
    "Four baselines: complete repartition \u2014 the "
    "naive upper bound on disturbance; greedy rescue "
    "\u2014 the cheapest possible repair; no repair at "
    "all \u2014 the quality floor; and the exact solver "
    "on small cases \u2014 the reference. The metrics "
    "cover recovery speed, schedule quality, and the "
    "cost of the disturbance itself."))
table(s, [
    ["Baselines", "Metrics"],
    ["Complete repartition \u2013 reschedule everything",
     "Recovery time, detect to resume"],
    ["Greedy rescue \u2013 reassign stranded tasks one by "
     "one", "Completion time and deadline success"],
    ["No repair \u2013 whatever survives", "Data "
     "re-shipped and communication cost"],
    ["Exact repair on small cases \u2013 the reference",
     "Tasks moved; repaired-schedule quality"],
], 0.9, 1.5, 11.5, 3.6, col_widths=[6.0, 5.5], size=14)
takeaway(s, "the platform from paper two already provides "
         "the baselines and the failure injection \u2014 "
         "the testbed exists")

s = slide("What I will vary, and what I expect", notes=(
    "We vary what makes recovery hard: where the failure "
    "hits \u2014 the critical path is the interesting "
    "case; how many machines fail at once; how much "
    "slack remains; and the scales from paper two. "
    "Three hypotheses, each falsifiable."))
bullets(s, [
    (0, "Failure injection:"),
    (1, "where \u2013 a machine on the critical path vs. "
        "a peripheral one"),
    (1, "how many \u2013 one machine vs. several at "
        "once"),
    (1, "when \u2013 how much deadline slack is left"),
    (0, "Scale: workflows of 10\u20131000 tasks, "
        "federations of 2\u201310 machines"),
    (0, "Hypotheses:"),
    (1, "H1 \u2013 recovery time grows with the region, "
        "not the whole workflow"),
    (1, "H2 \u2013 tasks moved and data re-shipped are "
        "far below the baselines at equal feasibility"),
    (1, "H3 \u2013 repair quality stays near the exact "
        "reference on small cases"),
], top=1.4, size=18)

s = slide("Twelve-month plan", notes=(
    "Four quarters: build, solve, evaluate, write. The "
    "deliverables land on the public repository, and the "
    "paper targets IPDPS or CCGrid."))
table(s, [
    ["Months", "Milestone", "Deliverable"],
    ["1\u20133", "Extend the simulator to machine "
     "failures; the boundary rule and region extraction; "
     "the complete-repartition baseline",
     "RQ1 done; baseline working"],
    ["4\u20136", "The repartition algorithm and "
     "replacement selection; incremental path updates",
     "RQ2 and RQ3 done"],
    ["7\u20139", "Full baseline comparison; exact "
     "reference on small cases; boundary sensitivity",
     "H1\u2013H3 tested"],
    ["10\u201312", "Write the paper; release the code "
     "publicly; submit",
     "Paper and artifact"],
], 0.9, 1.4, 11.5, 4.4, col_widths=[1.4, 7.0, 3.1],
    size=14)

s = slide("Risks, and how I will handle them", notes=(
    "Three honest risks. The boundary rule might expand "
    "to most of the workflow; incremental path updates "
    "might not pay off on small graphs; the region "
    "repair might trail the exact solver's quality. "
    "Each has a mitigation built into the plan."))
bullets(s, [
    (0, "The boundary rule might degenerate into "
        "'repartition everything'"),
    (1, "the size cap is enforced, and the sensitivity "
        "study measures it against failure location and "
        "slack"),
    (0, "Incremental path updates might not pay off on "
        "small graphs"),
    (1, "we measure the break-even point and keep full "
        "recomputation as a baseline"),
    (0, "Region repair might trail the exact solver's "
        "quality"),
    (1, "hybrid strategy: greedy repair at scale, exact "
        "repair where the region is small"),
], top=1.5, size=18)

# ==================================================================
# Conclusion
# ==================================================================
s = slide("Conclusion", notes=(
    "To conclude. The completed work gives a proved, "
    "data-aware formulation, four schedulers on one cost "
    "model, and a reproducible platform. The proposal "
    "adds three contributions: a principled boundary "
    "rule, minimal-region repartitioning, and the first "
    "use of incremental path updates for workflow "
    "recovery. Paper one placed the workflow, paper two "
    "priced its data and its approximation, and paper "
    "three keeps it alive when the infrastructure "
    "fails."))
bullets(s, [
    (0, "Already done: a proved, data-aware "
        "formulation, four schedulers on one cost "
        "model, and a reproducible platform (Papers 1 "
        "and 2)"),
    (0, "Proposed: a boundary rule for the smallest "
        "affected region (RQ1)"),
    (0, "Proposed: minimal-region repartitioning under "
        "a recovery cost model (RQ2)"),
    (0, "Proposed: incremental path updates for "
        "workflow recovery (RQ3)"),
    (0, "Expected outcome: recovery that is faster and "
        "less disturbing than a complete repartition, "
        "at near-reference quality"),
    (0, ""),
    (0, "Paper 1 placed the workflow; Paper 2 priced "
        "its data and approximation; Paper 3 keeps it "
        "alive when the infrastructure fails."),
], top=1.4, size=19)

# ---- closing ----
s = prs.slides.add_slide(BLANK)
_no += 1
tb = s.shapes.add_textbox(Inches(1), Inches(2.6), Inches(11.3),
                          Inches(1.2))
p = tb.text_frame.paragraphs[0]
p.text = "Thank you"
p.font.size = Pt(44)
p.font.bold = True
p.font.color.rgb = INK
p.alignment = PP_ALIGN.CENTER
sb = s.shapes.add_textbox(Inches(1), Inches(4.0), Inches(11.3),
                          Inches(1.4))
tf = sb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Questions and discussion"
p.font.size = Pt(20)
p.font.color.rgb = GREY
p.alignment = PP_ALIGN.CENTER
p = tf.add_paragraph()
p.text = "github.com/gayanigupta/data-aware-scheduling"
p.font.size = Pt(15)
p.font.color.rgb = GREY
p.alignment = PP_ALIGN.CENTER
s.notes_slide.notes_text_frame.text = "Questions welcome."

os.makedirs(os.path.dirname(OUT), exist_ok=True)
prs.save(OUT)
print("wrote", OUT, f"({len(prs.slides._sldIdLst)} slides)")
