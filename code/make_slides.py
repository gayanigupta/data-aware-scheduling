"""Build the proposal-defense slide deck (three-part research arc).

Part I   — published work: IEEE Cloud Summit 2025 paper
Part II  — current work:  data-aware approximate DAG scheduling (this repo)
Part III — proposed work: dynamic partial repartitioning after
           fog-resource failure

Generates slides/data-aware-scheduling.pptx with speaker notes on
every slide.  Run from the repo root:  python3 code/make_slides.py
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

# ------------------------------------------------------------------
# Colour scheme
# ------------------------------------------------------------------
NAVY   = RGBColor(0x0B, 0x2A, 0x4A)   # deep navy  — headers, dividers
TEAL   = RGBColor(0x0E, 0x7C, 0x7B)   # teal       — accents, part II
AMBER  = RGBColor(0xC7, 0x5B, 0x12)   # amber      — part III accent
GOLD   = RGBColor(0xE0, 0xA4, 0x1E)   # gold       — part I accent
PALE   = RGBColor(0xED, 0xF2, 0xF7)   # pale blue  — light panels
DARK   = RGBColor(0x23, 0x2B, 0x33)   # body text
GREY   = RGBColor(0x5A, 0x64, 0x6E)   # secondary text
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)

PAGE_W = Inches(13.333)
PAGE_H = Inches(7.5)
HDR_H  = Inches(0.95)

prs = Presentation()
prs.slide_width = PAGE_W
prs.slide_height = PAGE_H
BLANK = prs.slide_layouts[6]
_slide_no = 0
PART_TAG = ""


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def _rect(slide, l, t, w, h, color, line=False):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    if line:
        sh.line.color.rgb = color
    else:
        sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def _footer(slide, part, color):
    global _slide_no
    _slide_no += 1
    bar = slide.shapes.add_textbox(Inches(0.5), Inches(7.08),
                                   Inches(12.3), Inches(0.35))
    tf = bar.text_frame
    p = tf.paragraphs[0]
    p.text = part
    p.font.size = Pt(10)
    p.font.color.rgb = GREY
    p2 = slide.shapes.add_textbox(Inches(12.3), Inches(7.08),
                                  Inches(0.8), Inches(0.35))
    p = p2.text_frame.paragraphs[0]
    p.text = str(_slide_no)
    p.font.size = Pt(10)
    p.font.color.rgb = GREY
    p.alignment = PP_ALIGN.RIGHT


def add_slide(title=None, accent=NAVY, part="", notes=None):
    """Content slide: coloured header band + white body + footer."""
    s = prs.slides.add_slide(BLANK)
    if title:
        _rect(s, 0, 0, PAGE_W, HDR_H, accent)
        _rect(s, 0, HDR_H, Inches(0.18), PAGE_H - HDR_H, accent)
        tb = s.shapes.add_textbox(Inches(0.45), Inches(0.14),
                                  Inches(12.4), Inches(0.7))
        tb.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tb.text_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(26)
        p.font.bold = True
        p.font.color.rgb = WHITE
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    if part:
        _footer(s, part, accent)
    return s


def divider(part_label, title, subtitle, accent, notes=None):
    """Full-bleed section divider."""
    global _slide_no
    _slide_no += 1
    s = prs.slides.add_slide(BLANK)
    _rect(s, 0, 0, PAGE_W, PAGE_H, NAVY)
    _rect(s, 0, Inches(3.55), PAGE_W, Inches(0.09), accent)
    tag = s.shapes.add_textbox(Inches(1), Inches(2.0),
                               Inches(11.3), Inches(0.6))
    p = tag.text_frame.paragraphs[0]
    p.text = part_label
    p.font.size = Pt(20); p.font.bold = True; p.font.color.rgb = accent
    tb = s.shapes.add_textbox(Inches(1), Inches(2.7),
                              Inches(11.3), Inches(1.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(40); p.font.bold = True; p.font.color.rgb = WHITE
    sb = s.shapes.add_textbox(Inches(1), Inches(4.1),
                              Inches(11.3), Inches(1.6))
    tf = sb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = subtitle
    p.font.size = Pt(18); p.font.color.rgb = PALE
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def bullets(slide, items, left=0.65, top=1.25, width=7.0, height=5.6,
            size=17):
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
        p.space_after = Pt(7)
    return box


def callout(slide, text, left, top, width, height=1.0, fill=PALE,
            accent=TEAL, size=15):
    """Shaded call-out box with a coloured left edge."""
    _rect(slide, Inches(left), Inches(top), Inches(width),
          Inches(height), fill)
    _rect(slide, Inches(left), Inches(top), Inches(0.12),
          Inches(height), accent)
    tb = slide.shapes.add_textbox(Inches(left + 0.3), Inches(top + 0.08),
                                  Inches(width - 0.5),
                                  Inches(height - 0.16))
    tf = tb.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size); p.font.color.rgb = DARK


def box(slide, text, l, t, w, h, fill, text_color=WHITE, size=13,
        bold=False, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    sh = slide.shapes.add_shape(shape, Inches(l), Inches(t),
                                Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = NAVY
    sh.line.width = Pt(1)
    sh.shadow.inherit = False
    tf = sh.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size); p.font.bold = bold
    p.font.color.rgb = text_color
    p.alignment = PP_ALIGN.CENTER
    return sh


def arrow(slide, x1, y1, x2, y2, color=GREY, width=2.0, dashed=False):
    ln = slide.shapes.add_connector(
        2, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    ln.line.color.rgb = color
    ln.line.width = Pt(width)
    if dashed:
        ln.line.dash_style = 2  # DASH
    # add arrowhead
    lnEl = ln.line._get_or_add_ln()
    from pptx.oxml.ns import qn
    he = lnEl.makeelement(qn('a:headEnd'),
                          {'type': 'none'})
    te = lnEl.makeelement(qn('a:tailEnd'),
                          {'type': 'arrow', 'w': 'med', 'len': 'med'})
    lnEl.append(he); lnEl.append(te)
    return ln


def cross(slide, x, y, s, color=AMBER):
    """Draw an X over a failed node."""
    for dx, dy, ex, ey in [(0, 0, s, s), (0, s, s, 0)]:
        ln = slide.shapes.add_connector(
            1, Inches(x + dx), Inches(y + dy),
            Inches(x + ex), Inches(y + ey))
        ln.line.color.rgb = color
        ln.line.width = Pt(3)


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
    p.font.size = Pt(11)
    p.font.italic = True
    p.font.color.rgb = GREY
    p.alignment = PP_ALIGN.CENTER


def title_card(title_lines, sub_lines, accent, notes=None):
    """Master title slide with a colour band."""
    global _slide_no
    _slide_no += 1
    s = prs.slides.add_slide(BLANK)
    _rect(s, 0, 0, PAGE_W, Inches(0.35), NAVY)
    _rect(s, 0, Inches(0.35), PAGE_W, Inches(0.09), accent)
    _rect(s, 0, Inches(6.9), PAGE_W, Inches(0.6), NAVY)
    tb = s.shapes.add_textbox(Inches(0.9), Inches(1.5),
                              Inches(11.5), Inches(2.6))
    tf = tb.text_frame; tf.word_wrap = True
    for i, line in enumerate(title_lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line[0]
        p.font.size = Pt(line[1]); p.font.bold = True
        p.font.color.rgb = NAVY
        p.alignment = PP_ALIGN.CENTER
    sb = s.shapes.add_textbox(Inches(0.9), Inches(4.3),
                              Inches(11.5), Inches(2.3))
    tf = sb.text_frame; tf.word_wrap = True
    for i, line in enumerate(sub_lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line[0]
        p.font.size = Pt(line[1]); p.font.color.rgb = GREY
        p.alignment = PP_ALIGN.CENTER
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


P1 = "Part I  |  Published work — IEEE Cloud Summit 2025"
P2 = "Part II |  Current work — Data-aware approximate scheduling"
P3 = "Part III |  Proposed work — Partial repartitioning after failure"

# ==================================================================
# MASTER TITLE + ROADMAP
# ==================================================================
title_card(
    [("Scheduling Data-Intensive DAG Workflows", 36),
     ("across Federated Fog Systems", 36),
     ("— a three-part research arc —", 20)],
    [("Gayani Gupta, Amisha Gupta, Mohsen Amini Salehi,", 18),
     ("Antonio Fernandez Anta, Sanjukta Bhowmick, Jose Aguilar", 18),
     ("University of North Texas | UC Berkeley | IMDEA Networks | "
      "Universidad de Los Andes", 14),
     ("github.com/gayanigupta/data-aware-scheduling", 14)],
    TEAL,
    notes=("Welcome. This deck tells one continuous story in three "
           "parts: what we published at IEEE Cloud Summit 2025, the "
           "data-aware scheduling work that extends it, and the "
           "proposed next project — dynamic partial repartitioning "
           "after resource failure."))

s = add_slide("The road we will take", NAVY, "", notes=(
    "Three movements. Part I: the published foundation — federated "
    "fog scheduling with MILP, relaxation, greedy, and a genetic "
    "metaheuristic. Part II: this work — making the model truly "
    "data-aware, adding approximation, a bound, richer failure and "
    "bandwidth experiments, and an honest look at scale. Part III: "
    "the proposal — what happens when a whole fog resource fails "
    "mid-workflow."))
for i, (k, txt, c) in enumerate([
    ("PART I", "Published foundation — Efficient task allocation for "
     "DAG workflows across federated fog (IEEE Cloud Summit 2025)",
     GOLD),
    ("PART II", "Current work — Data-aware scheduling of approximate "
     "DAG workflows (this submission)", TEAL),
    ("PART III", "Proposed work — Dynamic partial repartitioning "
     "after fog-resource failure", AMBER)]):
    y = 1.6 + i * 1.7
    _rect(s, Inches(1.0), Inches(y), Inches(2.1), Inches(1.15), c)
    tb = s.shapes.add_textbox(Inches(1.0), Inches(y), Inches(2.1),
                              Inches(1.15))
    tf = tb.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = k
    p.font.size = Pt(18); p.font.bold = True; p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER
    tb2 = s.shapes.add_textbox(Inches(3.5), Inches(y), Inches(8.9),
                               Inches(1.15))
    tf2 = tb2.text_frame; tf2.word_wrap = True
    tf2.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf2.paragraphs[0]; p.text = txt
    p.font.size = Pt(18); p.font.color.rgb = DARK

# ==================================================================
# PART I — PUBLISHED WORK (IEEE Cloud Summit 2025)
# ==================================================================
divider("PART I", "Published Foundation",
        "Towards Efficient Allocation of Tasks in DAG-based Workflows "
        "across Federated Fog Systems — IEEE Cloud Summit 2025",
        GOLD, notes=(
    "Part I is the work already published at IEEE Cloud Summit 2025. "
    "It established the formulation and the four schedulers that "
    "everything else builds on."))

s = add_slide("The Compute Continuum", GOLD, P1, notes=(
    "The first paper framed fog scheduling inside the Compute "
    "Continuum: edge devices capture data, the federated fog tier "
    "runs latency-sensitive DAG tasks, and cloud/HPC provides "
    "elastic capacity for work that can tolerate the distance. Our "
    "paper focused on the fog tier — the most constrained, "
    "latency-sensitive part."))
bullets(s, [
    (0, "Three tiers cooperate to run a scientific workflow:"),
    (1, "Edge — sensors, acquisition, immediate preprocessing"),
    (1, "Federated fog — latency-sensitive DAG execution near the "
        "data"),
    (1, "Cloud / HPC — elastic capacity for non-urgent, heavy stages"),
    (0, "Placement is a three-way trade-off: compute capacity, "
        "data locality, network availability"),
    (0, "Our focus: the federated fog tier — where deadlines are "
        "tight and links are variable"),
], width=6.9)
pic(s, "federated-fog-architecture.png", 7.7, 1.35, width=5.2)
caption(s, "Federated fog tier in the compute continuum",
        7.7, 6.45, 5.2)

s = add_slide("The scheduling bottleneck we identified", GOLD, P1,
              notes=(
    "In the continuum, intermediate data must cross heterogeneous "
    "links of variable bandwidth. A placement that looks optimal on "
    "compute alone can blow the deadline because moving the input "
    "data costs more than the execution saves. Cloud-centric "
    "schedulers assume fat, stable links; in the fog that "
    "assumption breaks."))
bullets(s, [
    (0, "Every task placement is a high-stakes trade-off"),
    (0, "A 'fast' remote node can lose more time shipping the input "
        "than it saves executing"),
    (0, "Cloud-network assumptions (high, stable bandwidth) do not "
        "hold at the edge"),
    (0, "Disaster and monitoring workloads make it worse: the event "
        "that needs the answer also degrades the network"),
    (0, "No existing model jointly priced placement + data volume + "
        "per-link bandwidth + execution fractions"),
], width=12.0)

s = add_slide("The model we published", GOLD, P1, notes=(
    "The formulation: tasks T_i on resources f_a; edge data D_ji "
    "crossing link bandwidth B_ba gives delay D_ji over B_ba — zero "
    "if co-located. Eligibility matrix P_ia; non-preemptive tasks; "
    "approximate execution expressed as a fraction of full "
    "computation. Deadline t_max over all tasks."))
bullets(s, [
    (0, "DAG G = (T,E); task T_i, resource f_a, edge data D_ji"),
    (0, "Communication delay c = D_ji / B_ba when placed on "
        "different resources; 0 when co-located"),
    (0, "Eligibility P_ia — not every task can run everywhere"),
    (0, "Approximate execution: fraction of full computation -> "
        "fraction of accuracy"),
    (0, "Global deadline t_max; non-preemptive execution"),
    (0, "MILP with correctness proofs — the benchmark for "
        "everything that follows"),
], width=12.0)

s = add_slide("Four schedulers", GOLD, P1, notes=(
    "Four methods, same model: the exact MILP; a randomized "
    "relaxation that solves the continuous LP and rounds; a "
    "bandwidth- and data-aware greedy with a composite "
    "accuracy/critical-path priority; and a genetic metaheuristic "
    "searching the assignment-plus-fraction space."))
bullets(s, [
    (0, "MILP — global optimum; the reference point"),
    (0, "Randomized relaxation — solve the LP, round assignments, "
        "re-solve fractions"),
    (0, "Data-aware greedy — priority pi = a*A_i + (1-a)*CP_i; "
        "earliest-finish placement on ready tasks"),
    (0, "Genetic metaheuristic — chromosome = assignment + "
        "fractions; fitness rewards accuracy, penalizes lateness"),
], width=12.0)

s = add_slide("Orchestration: turning a solution into a system",
              GOLD, P1, notes=(
    "A placement solution needs an operational procedure around "
    "it. The journal framework adds an orchestration loop: gather "
    "static workflow state and dynamic resource state; a key rule — "
    "resource discovery must be coupled with data-path discovery; "
    "a powerful remote resource is useless if its prerequisites "
    "cannot arrive in time."))
bullets(s, [
    (0, "Static state: DAG, data sizes, execution profiles, "
        "eligibility, deadline, approximation requirements"),
    (0, "Dynamic state: availability, load, bandwidth estimates, "
        "reachability, policy"),
    (0, "Key rule: resource discovery is coupled with data-path "
        "discovery"),
    (1, "a stronger remote node is not a candidate unless its "
        "input can arrive in time"),
    (0, "Every decision is logged for provenance and "
        "reproducibility"),
], width=12.0)

s = add_slide("A scheduler-selection policy", GOLD, P1, notes=(
    "No single method wins everywhere, so we distilled the "
    "comparisons into an operational policy: MILP when the instance "
    "is small or stable; randomized relaxation when the workflow is "
    "large but quality matters; greedy for rapid local response; "
    "the GA when the search space is broad and planning time "
    "exists; and on failure or degradation, re-evaluate on the "
    "updated state."))
bullets(s, [
    (0, "Small/stable workflow, time to plan -> MILP"),
    (0, "Large workflow, quality-sensitive -> randomized "
        "relaxation"),
    (0, "Tight reaction deadline -> greedy"),
    (0, "Broad dynamic search space -> genetic metaheuristic"),
    (0, "Node failure / bandwidth loss / policy change -> "
        "re-evaluate on updated resource graph"),
    (0, ""),
    (0, "The policy makes the comparison operational, not just "
        "academic"),
], width=12.0)

s = add_slide("An adaptive execution and resilience loop", GOLD, P1,
              notes=(
    "Schedules are monitored, not fire-and-forget. Four steps: "
    "detect a change and identify affected tasks; update "
    "eligibility and transfer estimates; decide whether the "
    "remaining work can continue as-is or needs replanning; invoke "
    "the scheduler only for the unresolved tasks. Checkpoint-and-"
    "restart was named as a future extension."))
bullets(s, [
    (0, "1. Detect a state change; identify affected tasks and "
        "dependencies"),
    (0, "2. Update eligibility and communication estimates"),
    (0, "3. Decide: continue under the existing plan, or replan?"),
    (0, "4. Re-schedule only the unresolved tasks; record the "
        "reconfiguration"),
    (0, ""),
    (0, "Named but not yet built: checkpoint/restart, partial "
        "repair — the seed of Part III"),
], width=12.0)

s = add_slide("What the evaluation covered", GOLD, P1, notes=(
    "Four dimensions: deadline slack 1.0 to 2.0; federation size 2 "
    "to 10 nodes; workflow scale 10/100/1000 tasks; failure rates "
    "0 to 50 percent. Findings: MILP the quality reference; "
    "relaxation and GA track it best; greedy fastest but lowest "
    "accuracy under pressure; accuracy falls with failures."))
bullets(s, [
    (0, "Four dimensions of comparison:"),
    (1, "deadline slack alpha in [1.0, 2.0]"),
    (1, "federated fog nodes: 2, 4, 6, 8, 10"),
    (1, "workflow size: 10, 100, 1000 tasks"),
    (1, "workflow-node failure rate: 0% - 50%"),
    (0, "Published findings:"),
    (1, "MILP is the quality reference"),
    (1, "relaxation + GA track it most closely"),
    (1, "greedy is the low-overhead option under pressure"),
], width=12.0)

s = add_slide("What the first paper left open", GOLD, P1, notes=(
    "Honest gaps at the end of Part I: the failure model treated "
    "accuracy loss, not recovery; no bandwidth-degradation "
    "dimension; no explicit accuracy bound for comparison; "
    "scalability limits unexplored; and no recovery protocol — "
    "replanning was described, not built."))
bullets(s, [
    (0, "Failure study measured accuracy loss — not recovery"),
    (0, "No link-degradation dimension (what if bandwidth itself "
        "shrinks?)"),
    (0, "No explicit max-accuracy bound drawn against the methods"),
    (0, "Scalability limits of each solver left unquantified"),
    (0, "Recovery protocol described conceptually — not built"),
    (0, ""),
    (0, "Part II closes the first four. Part III attacks the last."),
], width=12.0)

# ==================================================================
# PART II — THIS PAPER
# ==================================================================
divider("PART II", "Data-Aware Scheduling of Approximate DAG "
        "Workflows in Federated Fog Systems",
        "Making the model honest: bounds, bandwidth degradation, "
        "retry semantics, scalability limits — and a reproducible "
        "artifact", TEAL, notes=(
    "Part II is the current work. Same core model — now hardened "
    "and stress-tested. The story: a disaster scenario, a joint "
    "formulation, four schedulers on one cost model, five "
    "experiments, and what the data actually says."))

s = add_slide("The scenario", TEAL, P2, notes=(
    "A river basin floods. The response workflow — sense, model, "
    "forecast, plan, alert — runs as a DAG. The deadline is hard: "
    "a forecast after the water is useless. And the cloud uplink "
    "is degraded or gone. The work must happen on fog computers "
    "near the disaster area."))
bullets(s, [
    (0, "A disaster unfolds: flood, wildfire, offshore incident"),
    (0, "The deadline is hard: a forecast that arrives late is a "
        "forecast nobody uses"),
    (0, "The uplink to the cloud is degraded or gone — the work "
        "must run on nearby fog machines"),
], width=12.0)
# drawn pipeline diagram
steps = [("SENSE", TEAL), ("MODEL", TEAL), ("FORECAST", TEAL),
         ("PLAN", TEAL), ("ALERT", GOLD)]
for i, (txt, c) in enumerate(steps):
    x = 0.9 + i * 2.45
    box(s, txt, x, 4.15, 1.9, 0.85, c, size=15, bold=True)
    if i:
        arrow(s, x - 0.5, 4.57, x, 4.57, NAVY, 2.25)
box(s, "deadline", 5.3, 5.5, 2.7, 0.6, NAVY, size=13, bold=True)
arrow(s, 6.65, 5.5, 6.65, 5.0, NAVY, 1.75)
box(s, "cloud uplink", 10.4, 5.55, 2.3, 0.75, PALE,
    text_color=GREY, size=13)
cross(s, 10.4, 5.55, 0.8)

s = add_slide("One fog site is not enough — so sites federate",
              TEAL, P2, notes=(
    "A single fog site rarely has capacity for the whole "
    "workflow. But nearby sites keep fast local links to each "
    "other even when the cloud link dies. Federating them creates "
    "a small local cloud — at the price of a placement choice for "
    "every task, where every choice ships data across a link."))
bullets(s, [
    (0, "Fog sites near the event: cell-tower racks, roadside "
        "cabinets, platform servers"),
    (0, "Individually too weak; but they keep fast, stable links "
        "to each other even when the cloud link fails"),
    (0, "Federation = a small local cloud built from nearby "
        "sites"),
    (0, "The catch: every task can now run in many places —"),
    (1, "and wherever it runs, its input data has to get there "
        "first"),
], width=6.9)
pic(s, "federated-fog-architecture.png", 7.7, 1.35, width=5.2)
caption(s, "Federated fog deployment around a disaster area",
        7.7, 6.45, 5.2)

s = add_slide("The workflow is a DAG — and data is the glue",
              TEAL, P2, notes=(
    "Tasks are nodes, dependencies are edges, and each edge "
    "carries data that must cross a link. Transfer time D over B "
    "can rival the task's own runtime — that is lever one. Lever "
    "two: tasks can run partially — a fraction l of the work costs "
    "l of the time and returns l of the accuracy."))
bullets(s, [
    (0, "Tasks = nodes, dependencies = edges (a DAG)"),
    (0, "Every edge carries data, D_ji, across a link of "
        "bandwidth B"),
    (1, "transfer time = D_ji / B  —  comparable to task "
        "runtime"),
    (0, "Tasks are approximate: running a fraction l costs l of "
        "the time and returns l of the accuracy"),
    (1, "a flood model at 80% fidelity still warns in time"),
], width=6.6)
pic(s, "disaster-response-dag.png", 7.4, 1.3, width=5.5)
caption(s, "Example disaster-response DAG used in the study",
        7.4, 6.5, 5.5)

s = add_slide("The problem, in one sentence", TEAL, P2, notes=(
    "Place every task on a node, choose how much of each to run, "
    "finish before the deadline, maximize accuracy. Two things "
    "make it hard: data movement rivals execution, and accuracy is "
    "a tradeable resource — and the two choices interact."))
bullets(s, [
    (0, "Assign every task to a fog node AND choose how much of "
        "it to run,"),
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

s = add_slide("Why existing schedulers do not fit", TEAL, P2, notes=(
    "HEFT — the classic reference — ranks tasks and places each "
    "where it finishes earliest, but assumes full execution and "
    "static edge weights. Fog schedulers do placement without "
    "approximation. Approximate-computing work trades quality for "
    "time without data movement. Nobody combined all three."))
bullets(s, [
    (0, "HEFT (Heterogeneous Earliest Finish Time): the classic "
        "DAG scheduler"),
    (1, "ranks tasks, places each where it finishes earliest"),
    (1, "but: full execution only; transfers are static edge "
        "weights"),
    (0, "Fog schedulers handle capacity and placement — but "
        "assume tasks always run completely"),
    (0, "Approximate-computing work trades quality for time — "
        "but ignores inter-node data movement"),
    (0, "Our gap: jointly optimize placement + data movement + "
        "execution fraction under one deadline"),
], width=12.0)

s = add_slide("The formulation: one MILP", TEAL, P2, notes=(
    "Decisions: assignment e_ia, fraction l_ia, implied start "
    "M_ia. Objective: average accuracy. Constraints: one eligible "
    "node per task; precedence waits for finish AND data arrival "
    "(the D over B term); completion inside the deadline. NP-hard "
    "— the MILP is the benchmark, and proofs plus a solver-ready "
    "linearization are in the paper."))
bullets(s, [
    (0, "Decisions: e_ia in {0,1} (task i on node a), l_ia in "
        "[0,1] (fraction), M_ia (start time)"),
    (0, "Objective: max (1/n) sum_i A_i sum_a l_ia — average "
        "accuracy"),
    (0, "One eligible node per task:  sum_a e_ia = 1"),
    (0, "Precedence + data: task i waits until every predecessor "
        "j finished AND D_ji/B_ba arrived"),
    (0, "Deadline: sum_a e_ia (M_ia + t_ia l_ia) <= t_max  for "
        "all i"),
    (0, "NP-hard even on unrelated parallel machines — the MILP "
        "is the benchmark, not the product"),
], width=12.0)

s = add_slide("Four schedulers, one cost model", TEAL, P2, notes=(
    "Because it is NP-hard: three scalable schedulers share the "
    "same communication-cost model — so differences are about the "
    "algorithm, not the accounting. LP rounding samples nodes "
    "from the fractional solution; greedy uses priority plus "
    "earliest finish with a fraction-retry; the GA searches "
    "assignments and fractions together."))
bullets(s, [
    (0, "MILP (HiGHS) — optimal at small/medium scale; the "
        "benchmark"),
    (0, "LP relaxation + randomized rounding"),
    (1, "relax e_ia to [0,1]; sample each task's node from the "
        "LP; re-solve the LP for fractions"),
    (0, "Data-aware greedy"),
    (1, "priority = beta*A_i + (1-beta)*critical-path; "
        "earliest-finish among ready tasks; on deadline miss, "
        "retry with a lower global fraction"),
    (0, "Genetic algorithm"),
    (1, "chromosome = assignment + per-task fractions; fitness "
        "rewards accuracy, penalizes lateness; co-location "
        "repair for heavy edges"),
], width=12.0)

s = add_slide("How we test it", TEAL, P2, notes=(
    "Discrete-event simulator, NumPy plus SciPy HiGHS. Parameters "
    "chosen so the regime is contested — a transfer can genuinely "
    "rival a task. Four datasets, five sweeps, five reps each. "
    "New in this work: the max-accuracy bound as the dashed-line "
    "yardstick, a retry-once failure model, a bandwidth-"
    "degradation sweep, and a blind baseline."))
bullets(s, [
    (0, "Discrete-event simulator (NumPy + SciPy HiGHS)"),
    (0, "Contested regime: t in [1,5], D in [5,50], B in [10,100] "
        "— a transfer can rival a task"),
    (0, "Datasets: 10/3, 100/5, 500/8, 1000/10 tasks-nodes; ~15% "
        "ineligible placements; ~2x speed range"),
    (0, "Five sweeps: slack | federation | workflow | failure | "
        "bandwidth"),
    (0, "Metric: average accuracy vs the max-accuracy bound "
        "(dashed); plus feasibility and wall time"),
    (0, "New baselines: max-accuracy bound; bandwidth-blind "
        "greedy"),
], width=6.9)
pic(s, "dataset_medium_graphs.png", 7.6, 1.35, width=5.4, base=RES)
caption(s, "A generated dataset (100 tasks / 5 nodes)",
        7.6, 6.55, 5.4)

s = add_slide("Five questions", TEAL, P2, notes=(
    "Each sweep isolates one variable. Slack: how tight is the "
    "deadline. Federation: how many nodes. Workflow: how many "
    "tasks. Failures: retry-once. Bandwidth: link degradation. "
    "Five fresh instances per point."))
bullets(s, [
    (0, "Q1  Deadline slack alpha in {1.0 ... 2.0} — how tight is "
        "the deadline?"),
    (0, "Q2  Federation size N in {2 ... 10} nodes — does "
        "capacity help?"),
    (0, "Q3  Workflow size n in {10, 100, 1000} — who scales?"),
    (0, "Q4  Failure rate in {0 ... 0.5}, retry-once — who stays "
        "feasible?"),
    (0, "Q5  Bandwidth x {1.0 ... 0.05} — what is data-awareness "
        "worth?"),
    (0, ""),
    (0, "5 fresh instances per point; means reported"),
], width=12.0)

s = add_slide("Q1 — Slack: the scheduler matters exactly when it "
              "hurts", TEAL, P2, notes=(
    "At alpha=1.0 the deadline barely fits: MILP leads at 1.38 vs "
    "bound 1.43; rounding 1.25, greedy 1.23, GA 1.20. From "
    "alpha=1.2 greedy reaches the bound; MILP by 1.5. Rounding "
    "and the GA trail 2.5-8% even at loose slack — a fixed search "
    "budget never quite recovers."))
pic(s, "perf_slack_accuracy.png", 0.7, 1.25, width=6.7)
bullets(s, [
    (0, "alpha = 1.0: MILP 1.38 vs bound 1.43; rounding 1.25, "
        "greedy 1.23, GA 1.20"),
    (0, "alpha >= 1.2: greedy reaches the bound; MILP joins by "
        "1.5"),
    (0, "Rounding and GA trail 2.5-8% even at alpha = 2.0 — a "
        "fixed budget cannot fully recover"),
    (0, "Lesson: method choice matters most exactly where the "
        "deadline binds"),
], left=7.7, width=5.1, top=1.4)

s = add_slide("Q2 — Federation: capacity buys feasibility, not "
              "accuracy", TEAL, P2, notes=(
    "Two to ten nodes. MILP and greedy on the bound at every "
    "size. GA drifts 1.5% to ~8% below; rounding similar. The "
    "placement space grows but the search budget is fixed — and "
    "extra nodes never exceed the bound: they buy feasible "
    "placements, not accuracy."))
pic(s, "perf_nodes_accuracy.png", 0.7, 1.25, width=6.7)
bullets(s, [
    (0, "MILP and greedy match the bound at every N"),
    (0, "GA: ~1.5% below bound at N=2 -> ~8% below at N=10; "
        "rounding similar (~8% at N=10)"),
    (0, "Reason: placement space grows with N but the search "
        "budget is fixed"),
    (0, "Extra nodes never exceed the bound — they buy "
        "feasibility, not accuracy"),
], left=7.7, width=5.1, top=1.4)

s = add_slide("Q3 — Workflow size: the simple greedy holds up "
              "best", TEAL, P2, notes=(
    "Scale the DAG. n=10: everyone on the bound. n=100: GA first "
    "to drift. n=1000: MILP past its cap; rounding survives at "
    "~93 s per LP re-solve; GA falls to 1.10 in ~159 s. The "
    "greedy stays on the bound in 0.15 seconds — the only method "
    "both fast and bound-level."))
pic(s, "perf_task_size_accuracy.png", 0.7, 1.25, width=6.7)
bullets(s, [
    (0, "n = 10: all methods on the bound (1.41)"),
    (0, "n = 100: MILP + greedy on bound; GA first to drift "
        "(1.26)"),
    (0, "n = 1000: MILP past the 800-var cap; greedy on bound in "
        "0.15 s; rounding 1.37 (~93 s/LP re-solve); GA 1.10 in "
        "~159 s"),
    (0, "GA budget is spread over a combinatorially growing "
        "space"),
], left=7.7, width=5.1, top=1.4)

s = add_slide("Same story on the four test datasets", TEAL, P2,
              notes=(
    "The per-dataset table agrees. Small/medium: everyone near "
    "the same score, greedy fastest with the shortest makespan. "
    "Large/xlarge: only greedy and GA fit; greedy keeps ~1.41 "
    "while the GA falls to 1.17 then 1.13, with a ~40% longer "
    "makespan and 73 seconds of search."))
bullets(s, [
    (0, "small (10/3): all four methods identical score 1.64; "
        "greedy fastest, shortest makespan (16.8 vs ~18)"),
    (0, "medium (100/5): MILP + greedy 1.44; rounding 1.32; GA "
        "1.27 — but greedy makespan 43.1 vs ~61"),
    (0, "large (500/8): only greedy + GA fit: 1.42 vs 1.17, "
        "makespan 50 vs 71"),
    (0, "xlarge (1000/10): greedy 1.41 in 0.14 s; GA 1.13 in "
        "73 s, makespan 120"),
    (0, ""),
    (0, "Accuracy is not free in wall time — and neither is the "
        "makespan"),
], width=12.0)

s = add_slide("Q4 — Failures: scores stay flat; feasibility is "
              "the story", TEAL, P2, notes=(
    "Retry-once: a failed task reruns in place; accuracy is kept "
    "if the retry still meets the deadline. Scores are flat — "
    "watch feasibility. Greedy stays feasible at every rate; "
    "MILP and GA ~60% at 0.5; rounding ~20%. Greedy's edge: it "
    "finishes early, so a retry fits inside the deadline."))
pic(s, "perf_failure_accuracy.png", 0.7, 1.25, width=6.7)
bullets(s, [
    (0, "Retry-once model: failed task reruns in place; accuracy "
        "kept if the retry meets the deadline"),
    (0, "Scores flat in failure rate — retries preserve "
        "accuracy"),
    (0, "Feasibility at rate 0.5: greedy 100%; MILP/GA ~60%; "
        "rounding ~20%"),
    (0, "Greedy's edge: it finishes early (makespan ~30 vs "
        "40-80), leaving room for retries"),
], left=7.7, width=5.1, top=1.4)

s = add_slide("Q5 — Link degradation: what data-awareness is "
              "worth", TEAL, P2, notes=(
    "Degrade every link down to 5% of nominal. The blind "
    "baseline is the cautionary tale: bound-level scores at every "
    "level — but the schedules are late (feasibility 80% -> 20% "
    "-> 0%). MILP stays feasible everywhere, ~10% score loss at "
    "0.05x; greedy feasible to 0.1x paying accuracy; GA fails at "
    "0.05x; rounding only above 0.5x."))
pic(s, "perf_bandwidth_accuracy.png", 0.7, 1.25, width=6.7)
bullets(s, [
    (0, "Bandwidth-blind greedy: bound-level scores at every "
        "level — but infeasible (80% at 0.5x, 20% at 0.2x, 0% "
        "below)"),
    (0, "MILP: feasible at all levels; ~10% score loss at "
        "0.05x"),
    (0, "Greedy: feasible to 0.1x, pays in accuracy; collapses "
        "at 0.05x"),
    (0, "GA: holds to 0.1x; rounding survives only above 0.5x"),
    (0, "High score + late = a missed alert, not a result"),
], left=7.7, width=5.1, top=1.4)

s = add_slide("Beyond the sweeps: 10^6-task structures", TEAL, P2,
              notes=(
    "Separately we stress-tested generation: million-task DAGs "
    "in ~3 s with depth growing like log n; million-node "
    "resource graphs in ~7 s, degree ~5. Structural instances "
    "only — schedulable dense instances stop where constraints "
    "and memory do."))
bullets(s, [
    (0, "DAG generator: 10^6 tasks / ~3M edges in ~3 s; depth "
        "grows like log n (24 -> 91 for 100 -> 10^6)"),
    (0, "Resource graphs: 10^6 fog nodes in ~7 s; avg degree "
        "~5, bandwidth 10-100"),
    (0, "Structural generation is cheap; schedulable dense "
        "instances stop where constraints do"),
    (1, "MILP: ~800 assignment vars; LP: ~10^5 rows at n=1000; "
        "dense instancing ~10^4 tasks"),
], width=6.9)
pic(s, "resource_graphs.png", 7.6, 1.35, width=5.4, base=RES)
caption(s, "Generated federated resource graphs (up to 10^6 "
           "nodes)", 7.6, 6.55, 5.4)

s = add_slide("What we learned", TEAL, P2, notes=(
    "Four takeaways: the scheduler matters most exactly where "
    "the deadline binds; accuracy under a binding deadline costs "
    "wall time; data-awareness buys feasibility, not score; and "
    "fixed search budgets decay. Rule of thumb: MILP at moderate "
    "scale, greedy at large scale."))
bullets(s, [
    (0, "1. The scheduler matters most exactly where the "
        "deadline binds — at loose slack almost anything works"),
    (0, "2. Accuracy under a binding deadline costs wall time: "
        "greedy 0.15 s vs rounding ~372 s vs GA ~159 s at "
        "n=1000"),
    (0, "3. Data-awareness buys feasibility, not score: the "
        "blind baseline's 'perfect' scores are late schedules"),
    (0, "4. Fixed search budgets decay — GA quality erodes with "
        "both n and N"),
    (0, ""),
    (0, "Rule of thumb: MILP at moderate scale, greedy at large "
        "scale, rounding/GA only where their cost is affordable"),
], width=12.0)

s = add_slide("Honest limits", TEAL, P2, notes=(
    "What we do not claim: the MILP is capped at ~800 assignment "
    "vars; the LP grows to ~10^5 rows at n=1000; the GA has one "
    "fixed budget; the failure model is retry-once-in-place — no "
    "replication, checkpointing, or migration. Dense schedulable "
    "instances stop near 10^4 tasks."))
bullets(s, [
    (0, "MILP capped at ~800 assignment variables — a deliberate "
        "boundary, not an oversight"),
    (0, "LP relaxation: ~10^5 constraint rows at n=1000; "
        "rounding trials reduced as size grows"),
    (0, "GA uses one fixed budget across all sizes — its gap is "
        "partly budget, partly search"),
    (0, "Failure model is retry-once-in-place — no replication, "
        "checkpointing, or cross-node migration yet"),
    (0, "Dense schedulable instances stop near 10^4 tasks; the "
        "10^6 experiments are structural"),
], width=12.0)

s = add_slide("Part II wrap-up", TEAL, P2, notes=(
    "One joint formulation, proved and linearized. Four "
    "schedulers on one cost model. Five sweeps with real data. "
    "MILP leads under pressure at moderate scale; the data-aware "
    "greedy is fast and bound-level at large scale. What it "
    "still cannot do: react to a resource failing mid-workflow. "
    "That is Part III."))
bullets(s, [
    (0, "One joint formulation: placement + execution fraction "
        "+ inter-node data movement, under a hard deadline"),
    (0, "Four schedulers sharing one cost model; five parameter "
        "sweeps; a bound at every scale"),
    (0, "MILP leads under pressure at moderate scale; the "
        "data-aware greedy is fast and bound-level at large "
        "scale"),
    (0, "Everything reproduces: code, CSVs, executed notebook, "
        "this deck"),
    (0, ""),
    (0, "Still open: the schedule is decided up front — what "
        "happens when a whole resource fails mid-workflow?"),
], width=12.0)

# ==================================================================
# PART III — PROPOSED RESEARCH
# ==================================================================
divider("PART III", "Proposed Research",
        "Dynamic Partial Repartitioning of DAG Workflows After "
        "Resource Failures in Federated Fog Environments",
        AMBER, notes=(
    "Part III is the proposal. Every experiment so far decided "
    "the schedule up front. Now: a fog resource fails while the "
    "workflow is running. The question is how to repair the "
    "smallest possible part."))

s = add_slide("From task failures to resource failures", AMBER, P3,
              notes=(
    "The failure sweep retried a task in place. The harder, "
    "real-world event is a whole resource dying — power loss, "
    "link cut, hardware failure — mid-execution. Unfinished "
    "tasks on it are stranded. The naive fix is to repartition "
    "everything: too slow, disturbs healthy tasks, wastes "
    "finished work. We want to repair only what broke."))
bullets(s, [
    (0, "Parts I-II: task-level failures, retry-once, assignment "
        "decided up front"),
    (0, "Reality in a disaster zone: whole fog resources die — "
        "power loss, link cut, hardware failure"),
    (0, "Unfinished tasks on the failed resource cannot "
        "continue"),
    (0, "Naive answer: repartition and reschedule the whole "
        "workflow —"),
    (1, "too slow; moves tasks that were running correctly; "
        "wastes completed work; adds migration traffic"),
    (0, "Our answer: repair only what broke"),
], width=12.0)

s = add_slide("The research question", AMBER, P3, notes=(
    "The proposal in one line, and the main research question."))
callout(s,
        "Dynamic Partial Repartitioning of DAG Workflows After "
        "Resource Failures in Federated Fog Environments",
        1.0, 1.4, 11.3, 1.0, PALE, AMBER, 17)
callout(s,
        "How can we quickly repartition and reschedule only the "
        "affected part of a DAG workflow after a fog resource "
        "fails — while reducing recovery time, communication "
        "cost, task movement, and workflow completion time?",
        1.0, 2.8, 11.3, 1.5, PALE, NAVY, 16)
bullets(s, [
    (0, "Preserve: completed tasks never restart; unaffected "
        "assignments never move"),
    (0, "Repair: only the smallest affected DAG region is "
        "repartitioned"),
], top=4.6, width=12.0)

s = add_slide("Two graphs, one coupling", AMBER, P3, notes=(
    "Two graphs: the task DAG and the infrastructure graph with "
    "resource attributes (capacity, memory, workload, "
    "availability) and link attributes (delay, bandwidth, "
    "transfer cost). The partition maps task groups to "
    "resources. A resource failure is a node deletion in one "
    "graph that must be repaired in the other."))
bullets(s, [
    (0, "Partition = which task group lives on which resource"),
    (0, "Resource attrs: capacity, memory, workload, "
        "availability"),
    (0, "Link attrs: delay, bandwidth, transfer cost"),
    (0, "A failure is a node deletion in one graph that must be "
        "repaired in the other"),
], width=12.0, top=1.15)
# --- drawn diagram: task DAG (left) coupled to infra graph (right)
ty = 3.3
box(s, "Task DAG", 1.0, ty - 0.7, 4.6, 0.5, NAVY, size=14, bold=True)
box(s, "Infra graph", 7.7, ty - 0.7, 4.6, 0.5, AMBER, size=14,
    bold=True)
# task nodes
tn = {"T1": (1.2, ty + 0.2), "T2": (3.2, ty - 0.15),
      "T3": (3.2, ty + 0.75), "T4": (5.2, ty + 0.3)}
for name, (x, y) in tn.items():
    box(s, name, x, y, 0.85, 0.6, PALE, text_color=NAVY,
        size=13, bold=True)
arrow(s, 2.05, ty + 0.5, 3.2, ty + 0.15, NAVY, 1.75)
arrow(s, 2.05, ty + 0.5, 3.2, ty + 1.05, NAVY, 1.75)
arrow(s, 4.05, ty + 0.15, 5.2, ty + 0.5, NAVY, 1.75)
arrow(s, 4.05, ty + 1.05, 5.2, ty + 0.7, NAVY, 1.75)
# infra nodes
rn = {"R1": (7.9, ty - 0.1), "R2": (9.9, ty - 0.35),
      "R3": (9.9, ty + 0.95), "R4": (11.9, ty + 0.3)}
for name, (x, y) in rn.items():
    box(s, name, x, y, 0.85, 0.6, PALE, text_color=AMBER,
        size=13, bold=True)
arrow(s, 8.75, ty + 0.2, 9.9, ty - 0.05, GREY, 1.5)
arrow(s, 8.75, ty + 0.2, 9.9, ty + 1.25, GREY, 1.5)
arrow(s, 10.75, ty - 0.05, 11.9, ty + 0.5, GREY, 1.5)
arrow(s, 10.75, ty + 1.25, 11.9, ty + 0.7, GREY, 1.5)
arrow(s, 10.32, ty + 0.25, 10.32, ty + 0.95, GREY, 1.5)
# partition mapping arrows (task -> resource)
arrow(s, 6.05, ty + 0.45, 7.9, ty + 0.2, TEAL, 2.0, dashed=True)
arrow(s, 5.6, ty + 0.95, 7.95, ty + 0.5, TEAL, 2.0, dashed=True)
tb = s.shapes.add_textbox(Inches(6.0), Inches(ty + 1.5),
                          Inches(4.5), Inches(0.5))
p = tb.text_frame.paragraphs[0]
p.text = "dashed = partition mapping"
p.font.size = Pt(11); p.font.italic = True; p.font.color.rgb = TEAL

s = add_slide("A resource fails mid-workflow", AMBER, P3, notes=(
    "Monitoring detects the failed node. Stranded unfinished "
    "tasks must be rescued; completed work is never redone. The "
    "subtle decision is the boundary: check parents and children "
    "of stranded tasks — sometimes dependents must move too, "
    "for data locality or to make the deadline."))
bullets(s, [
    (0, "Monitor detects the failure during execution"),
    (0, "Stranded unfinished tasks must be rescued"),
    (0, "Completed tasks never restart; unaffected tasks never "
        "move"),
    (0, "The boundary question: is rescuing just the stranded "
        "tasks enough, or must dependents move too?"),
], width=12.0, top=1.15)
# --- before / after mini infra graphs
for base_x, title, dead in [(1.0, "before", None),
                            (8.0, "after R2 fails", "R2")]:
    box(s, title, base_x, 3.35, 4.3, 0.5, NAVY, size=13, bold=True)
    pos = {"R1": (base_x + 0.1, 4.15), "R2": (base_x + 1.75, 3.95),
           "R3": (base_x + 1.75, 5.35), "R4": (base_x + 3.45, 4.6)}
    for name, (x, y) in pos.items():
        c = PALE if name != dead else GREY
        tc = NAVY if name != dead else WHITE
        box(s, name, x, y, 0.85, 0.6, c, text_color=tc, size=12,
            bold=True)
    arrow(s, base_x + 0.95, 4.45, base_x + 1.75, 4.25, GREY, 1.5)
    arrow(s, base_x + 0.95, 4.45, base_x + 1.75, 5.65, GREY, 1.5)
    arrow(s, base_x + 2.6, 4.25, base_x + 3.45, 4.9, GREY, 1.5)
    arrow(s, base_x + 2.6, 5.65, base_x + 3.45, 5.1, GREY, 1.5)
    if dead:
        cross(s, base_x + 1.75, 3.95, 0.85)
        box(s, "stranded tasks", base_x + 0.5, 6.15, 3.3, 0.55,
            AMBER, size=12, bold=True)
        arrow(s, base_x + 2.15, 6.15, base_x + 2.15, 4.6, AMBER,
              1.75, dashed=True)

s = add_slide("The method, step by step", AMBER, P3, notes=(
    "The pipeline: initial partition; detect failure; isolate "
    "stranded tasks; grow the minimal affected subgraph; pick "
    "replacement resources using shortest paths toward where "
    "parents and children live; repartition under exec time, "
    "comm delay, capacity, deadline, move cost, and load "
    "balance; assign; update only the affected paths; resume "
    "from the last good point."))
steps = [
    ("1", "Initial\npartition", NAVY),
    ("2", "Detect\nfailure", AMBER),
    ("3", "Isolate affected\nsubgraph", AMBER),
    ("4", "Pick replacement\nresources", AMBER),
    ("5", "Repartition\nthe region", AMBER),
    ("6", "Assign + update\npaths", TEAL),
    ("7", "Resume from\nlast good point", TEAL),
]
for i, (num, txt, c) in enumerate(steps):
    x = 0.55 + i * 1.82
    box(s, num, x, 2.0, 1.55, 0.55, c, size=16, bold=True)
    box(s, txt, x, 2.65, 1.55, 1.15, PALE, text_color=DARK,
        size=12)
    if i:
        arrow(s, x - 0.25, 3.2, x, 3.2, GREY, 2.0)
callout(s,
        "Repartition cost model: execution time + communication "
        "delay + data size + deadline + move cost + load balance",
        0.9, 4.5, 11.5, 0.9, PALE, AMBER, 14)
callout(s,
        "Rule throughout: completed tasks never restart, "
        "unaffected assignments never move — change as little of "
        "the original schedule as possible.",
        0.9, 5.6, 11.5, 0.9, PALE, NAVY, 14)

s = add_slide("Reuse, don't recompute: incremental shortest "
              "paths", AMBER, P3, notes=(
    "Moved tasks need new communication paths. Recomputing all "
    "shortest paths is the expensive part of recovery — so we "
    "build on Bhowmick's dynamic shortest-path work: update only "
    "the paths touched by the node deletion and the "
    "reassignment. That is what makes partial repair fast "
    "enough to matter."))
bullets(s, [
    (0, "Moved tasks need new communication paths to parents "
        "and children"),
    (0, "Recomputing all shortest paths on the infra graph is "
        "too slow mid-workflow"),
    (0, "Instead: dynamic/incremental shortest-path update "
        "(Bhowmick's dynamic SPT idea)"),
    (1, "update only paths touching the failed node and the "
        "moved tasks"),
    (0, "This is what makes partial repair fast enough to "
        "matter"),
], width=12.0)

s = add_slide("What is new", AMBER, P3, notes=(
    "The pieces exist separately: dynamic shortest-path "
    "updates, fog rescheduling, task redistribution on "
    "join/leave, partial workflow reconsideration — but nobody "
    "couples them. The novelty: map an infrastructure-node "
    "failure to the smallest affected DAG region, repartition "
    "only that, preserve everything else, and update paths "
    "incrementally."))
bullets(s, [
    (0, "Known: dynamic shortest-path updates (Bhowmick et "
        "al.) — but never applied to workflow repartitioning"),
    (0, "Known: fog rescheduling on uncertain events; task "
        "redistribution on node join/leave"),
    (0, "Known: partial workflow reconsideration — but without "
        "the two-graph coupling"),
    (0, ""),
    (0, "New: a dependency-aware method that maps an "
        "infra-node failure to the smallest affected DAG "
        "region,"),
    (1, "repartitions only that region, preserves unaffected "
        "assignments,"),
    (1, "and updates communication paths incrementally"),
], width=12.0)

s = add_slide("What the research must build", AMBER, P3, notes=(
    "The concrete contributions to defend: a boundary rule for "
    "the affected subgraph; a stay-or-move rule for dependents; "
    "the repartitioning algorithm; replacement-resource "
    "selection; incremental path updates; and minimization of "
    "movement and recovery time."))
bullets(s, [
    (0, "A principled boundary rule for the affected subgraph"),
    (0, "A stay-or-move decision for dependent tasks (data "
        "locality vs deadline)"),
    (0, "The repartitioning algorithm for the affected "
        "region"),
    (0, "Replacement-resource selection (capacity, memory, "
        "paths)"),
    (0, "Incremental communication-path updates"),
    (0, "Minimization of task movement and recovery time — "
        "with guarantees or strong evidence"),
], width=12.0)

s = add_slide("How we will evaluate it", AMBER, P3, notes=(
    "Four baselines — complete repartition, greedy recovery, "
    "static scheduling, and the MILP for small cases (this "
    "paper's stack supplies it). Metrics: recovery time, "
    "makespan, communication cost, tasks moved, data moved, "
    "energy, deadline success, repaired-schedule quality. Same "
    "simulator, same failure injection — the platform already "
    "exists."))
bullets(s, [
    (0, "Baselines: complete repartition | greedy recovery | "
        "static schedule | MILP (small cases — Part II's "
        "stack)"),
    (0, "Metrics:"),
    (1, "failure-recovery time, workflow completion time"),
    (1, "communication cost, tasks moved, data transferred"),
    (1, "energy, deadline success rate, repaired-schedule "
        "quality"),
    (0, "Same simulator, same failure injection — Part II's "
        "platform is the testbed"),
], width=12.0)

s = add_slide("The arc: paper 1 -> paper 2 -> proposal", AMBER, P3,
              notes=(
    "The continuity in one slide. Paper 1 established the model "
    "and four schedulers. Paper 2 hardened it — bound, retry "
    "semantics, bandwidth degradation, honest scale limits. "
    "The proposal changes the failure granularity from task "
    "retry to resource loss, and the scheduling granularity "
    "from whole-DAG placement to minimal-region repair. Same "
    "two graphs, same cost model — and the baselines are "
    "already built."))
for i, (k, txt, c) in enumerate([
    ("PAPER 1", "Efficient DAG task allocation across federated "
     "fog — model + 4 schedulers (IEEE Cloud Summit 2025)",
     GOLD),
    ("PAPER 2", "Data-aware approximate scheduling — bound, "
     "retry, bandwidth, scale limits + artifact (this work)",
     TEAL),
    ("PROPOSED", "Partial repartitioning after resource failure "
     "— minimal-region repair, incremental paths", AMBER)]):
    y = 1.5 + i * 1.75
    _rect(s, Inches(0.8), Inches(y), Inches(2.4), Inches(1.25), c)
    tb = s.shapes.add_textbox(Inches(0.8), Inches(y), Inches(2.4),
                              Inches(1.25))
    tf = tb.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = k
    p.font.size = Pt(16); p.font.bold = True
    p.font.color.rgb = WHITE; p.alignment = PP_ALIGN.CENTER
    tb2 = s.shapes.add_textbox(Inches(3.6), Inches(y), Inches(9.0),
                               Inches(1.25))
    tf2 = tb2.text_frame; tf2.word_wrap = True
    tf2.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf2.paragraphs[0]; p.text = txt
    p.font.size = Pt(16); p.font.color.rgb = DARK

# ==================================================================
# CLOSING
# ==================================================================
s = add_slide(notes="Questions welcome. Thank you.")
_rect(s, 0, 0, PAGE_W, PAGE_H, NAVY)
_rect(s, 0, Inches(3.4), PAGE_W, Inches(0.09), TEAL)
tb = s.shapes.add_textbox(Inches(1), Inches(2.5), Inches(11.3),
                          Inches(1.2))
p = tb.text_frame.paragraphs[0]
p.text = "Thank you"
p.font.size = Pt(48); p.font.bold = True; p.font.color.rgb = WHITE
p.alignment = PP_ALIGN.CENTER
sb = s.shapes.add_textbox(Inches(1), Inches(4.0), Inches(11.3),
                          Inches(1.6))
tf = sb.text_frame; tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Questions & discussion"
p.font.size = Pt(20); p.font.color.rgb = PALE
p.alignment = PP_ALIGN.CENTER
p = tf.add_paragraph()
p.text = "github.com/gayanigupta/data-aware-scheduling"
p.font.size = Pt(15); p.font.color.rgb = GOLD
p.alignment = PP_ALIGN.CENTER


os.makedirs(os.path.dirname(OUT), exist_ok=True)
prs.save(OUT)
print("wrote", OUT, f"({len(prs.slides._sldIdLst)} slides)")
