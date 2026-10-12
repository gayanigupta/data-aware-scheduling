"""Build the PhD proposal-defense slide deck.

Structure (standard proposal-defense spine):
  1. Introduction & motivation
  2. Related work and the research gap
  3. Problem definition (formal)
  4. Completed work & preliminary results (Parts I + II)
  5. Proposed research (Part III: partial repartitioning)
  6. Evaluation plan & timeline
  7. Conclusion

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
NAVY   = RGBColor(0x0B, 0x2A, 0x4A)
TEAL   = RGBColor(0x0E, 0x7C, 0x7B)
AMBER  = RGBColor(0xC7, 0x5B, 0x12)
GOLD   = RGBColor(0xE0, 0xA4, 0x1E)
PALE   = RGBColor(0xED, 0xF2, 0xF7)
DARK   = RGBColor(0x23, 0x2B, 0x33)
GREY   = RGBColor(0x5A, 0x64, 0x6E)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)

PAGE_W = Inches(13.333)
PAGE_H = Inches(7.5)
HDR_H  = Inches(0.95)

prs = Presentation()
prs.slide_width = PAGE_W
prs.slide_height = PAGE_H
BLANK = prs.slide_layouts[6]
_slide_no = 0


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


def _footer(slide, part):
    global _slide_no
    _slide_no += 1
    bar = slide.shapes.add_textbox(Inches(0.5), Inches(7.08),
                                   Inches(11.5), Inches(0.35))
    p = bar.text_frame.paragraphs[0]
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
    s = prs.slides.add_slide(BLANK)
    if title:
        _rect(s, 0, 0, PAGE_W, HDR_H, accent)
        _rect(s, 0, HDR_H, Inches(0.18), PAGE_H - HDR_H, accent)
        tb = s.shapes.add_textbox(Inches(0.45), Inches(0.14),
                                  Inches(12.4), Inches(0.7))
        tb.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tb.text_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(27)
        p.font.bold = True
        p.font.color.rgb = WHITE
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    if part:
        _footer(s, part)
    return s


def divider(part_label, title, subtitle, accent, notes=None):
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
    p.font.size = Pt(19); p.font.color.rgb = PALE
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def bullets(slide, items, left=0.65, top=1.25, width=7.0, height=5.6,
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


def callout(slide, text, left, top, width, height=1.0, fill=PALE,
            accent=TEAL, size=15, bold=False, text_color=DARK):
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
    p.font.size = Pt(size); p.font.bold = bold
    p.font.color.rgb = text_color


def takeaway(slide, text, left=0.7, top=5.95, width=11.9, height=0.95,
             accent=GOLD):
    callout(slide, "Take-away:  " + text, left, top, width, height,
            PALE, accent, 15, bold=False)


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
        ln.line.dash_style = 2
    lnEl = ln.line._get_or_add_ln()
    from pptx.oxml.ns import qn
    he = lnEl.makeelement(qn('a:headEnd'), {'type': 'none'})
    te = lnEl.makeelement(qn('a:tailEnd'),
                          {'type': 'arrow', 'w': 'med', 'len': 'med'})
    lnEl.append(he); lnEl.append(te)
    return ln


def cross(slide, x, y, s, color=AMBER):
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
    box_ = slide.shapes.add_textbox(Inches(left), Inches(top),
                                    Inches(width), Inches(0.6))
    p = box_.text_frame.paragraphs[0]
    p.text = text
    p.font.size = Pt(12)
    p.font.italic = True
    p.font.color.rgb = GREY
    p.alignment = PP_ALIGN.CENTER


def table(slide, rows, l, t, w, h, col_widths=None, size=13,
          header_fill=NAVY, header_color=WHITE, body_fill=WHITE):
    nr, nc = len(rows), len(rows[0])
    gfx = slide.shapes.add_table(nr, nc, Inches(l), Inches(t),
                                 Inches(w), Inches(h))
    tbl = gfx.table
    if col_widths:
        for i, cw in enumerate(col_widths):
            tbl.columns[i].width = Inches(cw)
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = tbl.cell(ri, ci)
            cell.fill.solid()
            cell.fill.fore_color.rgb = header_fill if ri == 0 \
                else (PALE if ri % 2 == 0 else body_fill)
            cell.margin_top = Pt(3); cell.margin_bottom = Pt(3)
            cell.margin_left = Pt(6); cell.margin_right = Pt(6)
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = str(val)
            p.font.size = Pt(size)
            p.font.bold = ri == 0
            p.font.color.rgb = header_color if ri == 0 else DARK
    return tbl


def title_card(title_lines, sub_lines, accent, notes=None):
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


S1 = "1  |  Introduction & motivation"
S2 = "2  |  Related work"
S3 = "3  |  Problem definition"
S4 = "4  |  Completed work & preliminary results"
S5 = "5  |  Proposed research"
S6 = "6  |  Evaluation plan & timeline"
S7 = "7  |  Conclusion"

# ==================================================================
# TITLE + OUTLINE
# ==================================================================
title_card(
    [("Dynamic Partial Repartitioning of DAG Workflows", 34),
     ("After Resource Failures in Federated Fog Environments", 34),
     ("PhD Research Proposal", 20)],
    [("Gayani Gupta", 18),
     ("Department of Computer Science and Engineering, "
      "University of North Texas", 16),
     ("Advisors: Dr. Mohsen Amini Salehi and Dr. Sanjukta "
      "Bhowmick", 15),
     ("github.com/gayanigupta/data-aware-scheduling", 13)],
    NAVY,
    notes=("Good morning everyone. I am going to walk you through "
           "my PhD proposal. The talk runs in seven parts: the "
           "motivation, the related work and the gap, a precise "
           "problem statement, the work we have already finished "
           "and what it showed, the research I am proposing, how "
           "I plan to evaluate it and when, and finally what the "
           "work contributes."))

s = add_slide("Outline", NAVY, "", notes=(
    "The first three sections set the problem up. Section four "
    "reports the completed work, which is two papers at this "
    "point. Sections five and six are the proposal itself, and "
    "the last section is what the work contributes."))
for i, txt in enumerate([
        "1   Introduction and motivation",
        "2   Related work, and what is still missing",
        "3   Problem definition",
        "4   Completed work and preliminary results",
        "5   Proposed research: dynamic partial repartitioning",
        "6   Evaluation plan and timeline",
        "7   Conclusion: expected contributions"]):
    y = 1.15 + i * 0.78
    _rect(s, Inches(1.2), Inches(y), Inches(0.14), Inches(0.6),
          [NAVY, NAVY, NAVY, TEAL, AMBER, AMBER, NAVY][i])
    tb = s.shapes.add_textbox(Inches(1.6), Inches(y), Inches(10.5),
                              Inches(0.6))
    tb.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tb.text_frame.paragraphs[0]
    p.text = txt
    p.font.size = Pt(20)
    p.font.color.rgb = DARK
    p.font.bold = i in (3, 4)

# ==================================================================
# SECTION 1 — INTRODUCTION & MOTIVATION
# ==================================================================
divider("1  |  INTRODUCTION & MOTIVATION", "Why this problem matters",
        "Time-critical workflows, unreliable networks, and the "
        "case for the federated fog", NAVY, notes=(
    "Section one. The motivation in one paragraph: time-critical "
    "workflows have to run exactly when the network is at its "
    "worst, and nearby fog machines, federated together, are the "
    "only capacity left."))

s = add_slide("The scenario", NAVY, S1, notes=(
    "Imagine a river basin starting to flood. The response "
    "workflow, sense, model, forecast, plan, alert, runs as a "
    "DAG of dependent tasks. The deadline is not a preference: "
    "a forecast that arrives after the water has risen is a "
    "forecast nobody uses. And the same event that creates the "
    "deadline also degrades or kills the link to the cloud."))
bullets(s, [
    (0, "A disaster is unfolding: a flood, a wildfire, an "
        "offshore incident"),
    (0, "The deadline is hard. A forecast that arrives late is "
        "a forecast nobody uses"),
    (0, "And the same event that creates the deadline also "
        "degrades or kills the link to the cloud"),
], width=12.0)
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

s = add_slide("Federation is the answer, and it comes with a "
              "scheduling price", NAVY, S1, notes=(
    "A single fog site is rarely strong enough for the whole "
    "workflow. But nearby sites keep fast, stable links to each "
    "other even when the cloud link dies, so federating them "
    "creates a small local cloud. The price is a placement "
    "choice for every task, and every choice moves data across "
    "a link."))
bullets(s, [
    (0, "The fog sites near an event are things like cell-tower "
        "racks, roadside cabinets, platform servers"),
    (0, "Each one alone is too weak for the whole workflow"),
    (0, "But they keep fast, stable links to each other even "
        "when the cloud link fails"),
    (0, "Federating them creates a small local cloud"),
    (0, "The price: every task can now run in many places, and "
        "wherever it runs, its input data has to get there "
        "first"),
], width=6.9)
pic(s, "federated-fog-architecture.png", 7.7, 1.35, width=5.2)
caption(s, "Federated fog deployment around a disaster area",
        7.7, 6.45, 5.2)

s = add_slide("Two decisions, and they interact", NAVY, S1,
              notes=(
    "Two things make this problem genuinely hard. The first is "
    "data movement: every edge of the DAG carries data, and "
    "moving it across a link can take as long as the task "
    "itself, so the fastest node can end up being the worst "
    "choice. The second is approximation: tasks can run "
    "partially, a fraction of the work for a fraction of the "
    "accuracy. And the two interact, because placement decides "
    "the transfers while fractions decide the runtimes."))
bullets(s, [
    (0, "Data movement rivals computation"),
    (1, "every edge carries D_ji across a link of bandwidth B, "
        "so a transfer takes D_ji / B, often as long as the "
        "task itself"),
    (0, "Accuracy is a tradeable resource"),
    (1, "running a fraction l of a task costs l of the time "
        "and returns l of the accuracy; a flood model at 80% "
        "fidelity still warns in time"),
    (0, "And the two interact: placement decides the "
        "transfers, fractions decide the runtimes"),
], width=12.0)

s = add_slide("The dissertation as three papers", NAVY, S1,
              notes=(
    "The whole PhD is three papers on one arc. The first, "
    "published at Cloud Summit 2025, built the model and four "
    "schedulers. The second hardened it: data-aware, bounded, "
    "stress-tested. The third, which is this proposal, repairs "
    "the smallest affected region when a whole resource fails. "
    "Each paper answers the question the previous one left "
    "open."))
for i, (k, txt, c) in enumerate([
    ("PAPER 1", "Efficient DAG task allocation across "
     "federated fog: the model plus four schedulers.  "
     "Published at IEEE Cloud Summit 2025", TEAL),
    ("PAPER 2", "Data-aware scheduling of approximate DAG "
     "workflows: an accuracy bound, retry semantics, "
     "bandwidth degradation, scalability limits.  "
     "In revision for CCGrid 2027", TEAL),
    ("PAPER 3", "Dynamic partial repartitioning after a "
     "resource fails mid-workflow.  This proposal; the "
     "target is IPDPS or CCGrid 2028", AMBER)]):
    y = 1.5 + i * 1.75
    _rect(s, Inches(0.8), Inches(y), Inches(2.4), Inches(1.25), c)
    tb = s.shapes.add_textbox(Inches(0.8), Inches(y), Inches(2.4),
                              Inches(1.25))
    tf = tb.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = k
    p.font.size = Pt(15); p.font.bold = True
    p.font.color.rgb = WHITE; p.alignment = PP_ALIGN.CENTER
    tb2 = s.shapes.add_textbox(Inches(3.6), Inches(y), Inches(9.0),
                               Inches(1.25))
    tf2 = tb2.text_frame; tf2.word_wrap = True
    tf2.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf2.paragraphs[0]; p.text = txt
    p.font.size = Pt(16); p.font.color.rgb = DARK

# ==================================================================
# SECTION 2 — RELATED WORK
# ==================================================================
divider("2  |  RELATED WORK", "What is known, and what is missing",
        "Four research threads converge; none covers the whole "
        "problem", NAVY, notes=(
    "Section two. I will go through four threads of related "
    "work: classic DAG scheduling, fog and edge placement, "
    "approximate computing, and failure recovery. Then the gap "
    "in one table."))

s = add_slide("Classic DAG scheduling", NAVY, S2, notes=(
    "The reference point is HEFT: rank the tasks, place each "
    "one where it finishes earliest. It is a great algorithm, "
    "but it assumes tasks always run completely, transfers are "
    "static edge weights, and the plan is fixed before "
    "execution starts."))
bullets(s, [
    (0, "HEFT (Topcuoglu et al., 2002) is the reference "
        "algorithm: rank tasks, place each where it finishes "
        "earliest"),
    (0, "CPOP, PEFT and the rest of that family refine the "
        "same template"),
    (0, "But all of them assume tasks run completely, "
        "transfers are static edge weights, and the plan is "
        "fixed before execution starts"),
    (0, "Federated-fog variants add eligibility and "
        "federation constraints; that is where our first "
        "paper sits"),
], width=12.0)

s = add_slide("Fog and edge scheduling", NAVY, S2, notes=(
    "The fog scheduling literature handles capacity, "
    "eligibility and heterogeneity across the continuum. What "
    "it does not do, for the most part, is treat data movement "
    "as a first-class cost, and it treats tasks as atomic: run "
    "completely or not at all."))
bullets(s, [
    (0, "Fog schedulers handle capacity, eligibility and "
        "heterogeneity across the edge, fog and cloud tiers"),
    (0, "Surveys like Mouradian et al. (2018) catalog the "
        "placement policies"),
    (0, "Locality is priced in, but per-link bandwidth "
        "rarely is"),
    (0, "And tasks are atomic: they run completely or not "
        "at all"),
    (0, "Failures are handled by restarting, not by "
        "repairing"),
], width=12.0)

s = add_slide("Approximate computing", NAVY, S2, notes=(
    "Approximate computing trades quality for time, which is "
    "exactly what a tight deadline needs. But that literature "
    "assumes the data is already sitting where it needs to be; "
    "the cost of moving it is not part of the trade."))
bullets(s, [
    (0, "Trades result quality for time or energy: loop "
        "truncation, reduced precision, early termination"),
    (0, "That makes accuracy a schedulable resource, which "
        "is exactly what a tight deadline needs"),
    (0, "But the literature assumes the data is already "
        "where it needs to be; the transfer cost is not "
        "part of the trade"),
    (0, "We put the two together: approximation and data "
        "movement in one model"),
], width=12.0)

s = add_slide("Failure recovery and rescheduling", NAVY, S2,
              notes=(
    "This is the thread closest to the proposal. Rescheduling "
    "work reconsiders a workflow at chosen points but remaps "
    "it globally. Fog studies redistribute tasks when nodes "
    "join or leave. And on the graph side, dynamic "
    "shortest-path updates repair routing after a change. "
    "None of them couples a node failure to the smallest "
    "affected region of the task DAG."))
bullets(s, [
    (0, "Workflow rescheduling (Sakellariou and Zhao, 2004) "
        "reconsiders the plan at chosen points, but remaps it "
        "globally"),
    (0, "Fog studies redistribute tasks when nodes join or "
        "leave, or when uncertain events hit"),
    (0, "Checkpointing and replication recover the work, "
        "at a real recompute or replication cost"),
    (0, "Dynamic shortest-path updates (Riazi, Khanda, "
        "Bhowmick and colleagues) repair routing after a "
        "graph change; nobody has used them for workflow "
        "repartitioning"),
], width=12.0)

s = add_slide("The gap, in one table", NAVY, S2, notes=(
    "Read each column as a capability. The classic schedulers "
    "place tasks but neither price data per link nor "
    "approximate nor repair. Fog schedulers add some data "
    "awareness. Our first two papers add approximation. The "
    "last column, repairing only the affected region after a "
    "resource fails, is empty. That is the proposal."))
table(s, [
    ["Capability", "HEFT / classic", "Fog schedulers",
     "Papers 1 + 2", "Proposed work"],
    ["Placement on heterogeneous nodes", "yes", "yes", "yes",
     "yes"],
    ["Per-edge data + per-link bandwidth", "no", "partial",
     "yes", "yes"],
    ["Approximate execution fractions", "no", "no", "yes",
     "yes"],
    ["Recovery after resource failure", "restart",
     "reschedule all", "retry task", "repair region only"],
], 0.8, 1.35, 11.7, 3.4,
    col_widths=[4.3, 1.85, 1.85, 1.85, 1.85], size=14)
callout(s, "The gap: nobody couples an infrastructure-node "
        "failure to the smallest affected region of the task "
        "DAG.", 0.8, 5.3, 11.7, 0.95, PALE, AMBER, 16,
        bold=True)

# ==================================================================
# SECTION 3 — PROBLEM DEFINITION
# ==================================================================
divider("3  |  PROBLEM DEFINITION", "The problem, stated precisely",
        "Two graphs, one coupling, a hard deadline", NAVY, notes=(
    "Section three. Before any algorithm, let me define the "
    "system model and state the problem formally, both the "
    "static core that the completed work solved and the dynamic "
    "extension this proposal adds."))

s = add_slide("System model: two graphs", NAVY, S3, notes=(
    "Two graphs. The task graph has the work: execution times, "
    "accuracies, eligibility, and data on every edge. The "
    "infrastructure graph has the machines and the links "
    "between them. A partition maps one onto the other; a "
    "failure deletes a node from one graph and strands work in "
    "the other."))
bullets(s, [
    (0, "Task graph G_T = (T, E): each task has an execution "
        "time, a full-run accuracy, and a set of nodes it is "
        "allowed to run on"),
    (1, "every edge carries D_ji bytes of dependency data"),
    (0, "Infrastructure graph G_R = (R, L): each node has "
        "capacity, memory and availability; each link has "
        "bandwidth and delay"),
    (0, "A partition pi maps tasks onto nodes, one eligible "
        "node per task"),
    (0, "A failure deletes a node from G_R and strands work "
        "in G_T"),
], width=6.9, size=16)
ty = 3.3
box(s, "Task DAG  G_T", 7.55, ty - 0.7, 2.4, 0.5, NAVY,
    size=13, bold=True)
box(s, "Infra  G_R", 10.3, ty - 0.7, 2.4, 0.5, AMBER,
    size=13, bold=True)
tn = {"T1": (7.6, ty + 0.2), "T2": (8.7, ty - 0.15),
      "T3": (8.7, ty + 0.75), "T4": (9.8, ty + 0.3)}
for name, (x, y) in tn.items():
    box(s, name, x, y, 0.7, 0.55, PALE, text_color=NAVY,
        size=11, bold=True)
arrow(s, 8.3, ty + 0.48, 8.7, ty + 0.15, NAVY, 1.5)
arrow(s, 8.3, ty + 0.48, 8.7, ty + 1.0, NAVY, 1.5)
arrow(s, 9.4, ty + 0.13, 9.8, ty + 0.5, NAVY, 1.5)
arrow(s, 9.4, ty + 1.03, 9.8, ty + 0.75, NAVY, 1.5)
rn = {"R1": (10.35, ty + 0.2), "R2": (11.4, ty - 0.15),
      "R3": (11.4, ty + 0.75), "R4": (12.45, ty + 0.3)}
for name, (x, y) in rn.items():
    box(s, name, x, y, 0.7, 0.55, PALE, text_color=AMBER,
        size=11, bold=True)
arrow(s, 11.05, ty + 0.48, 11.4, ty + 0.15, GREY, 1.25)
arrow(s, 11.05, ty + 0.48, 11.4, ty + 1.0, GREY, 1.25)
arrow(s, 12.1, ty + 0.13, 12.45, ty + 0.5, GREY, 1.25)
arrow(s, 12.1, ty + 1.03, 12.45, ty + 0.75, GREY, 1.25)
arrow(s, 10.5, ty + 0.48, 10.35, ty + 0.48, TEAL, 1.75,
      dashed=True)

s = add_slide("The static core of the problem", NAVY, S3,
              notes=(
    "The completed work solved this problem: given the two "
    "graphs and a deadline, choose where each task runs and how "
    "much of it runs, finish before the deadline, and maximize "
    "the average accuracy. It is NP-hard, so the exact solver "
    "is the benchmark, not the product."))
callout(s, "GIVEN   the two graphs (tasks with times, "
        "accuracies, eligibility; nodes with capacities, links "
        "with bandwidths) and a deadline t_max",
        0.8, 1.35, 11.7, 0.9, PALE, NAVY, 15)
callout(s, "DECIDE   for every task: which eligible node it "
        "runs on (e_ia) and how much of it runs (l_ia)",
        0.8, 2.4, 11.7, 0.9, PALE, TEAL, 15)
callout(s, "SUBJECT TO   one node per task; predecessors "
        "finish and their data arrives first; everything done "
        "by the deadline", 0.8, 3.45, 11.7, 0.9, PALE, GREY, 15)
callout(s, "MAXIMIZE   the average accuracy  A_bar = (1/n) "
        "sum_i A_i l_i", 0.8, 4.5, 11.7, 0.9, PALE, GOLD, 15,
        bold=True)
bullets(s, [
    (0, "It is NP-hard even on unrelated parallel machines, "
        "so the exact solver is the benchmark, not the "
        "product"),
], top=5.7, width=12.0, size=15)

s = add_slide("The dynamic extension (the proposal)", NAVY, S3,
              notes=(
    "The proposal adds one event to the same model: at time "
    "tau a resource fails. The unfinished tasks on it are "
    "stranded. Now the question is which part of the DAG "
    "actually needs repair and where the stranded work should "
    "go, at minimum disturbance. Done work is never redone and "
    "healthy placements never move."))
callout(s, "EVENT   at time tau, resource r* fails; the "
        "unfinished tasks on it are stranded",
        0.8, 1.35, 11.7, 0.9, PALE, AMBER, 15)
callout(s, "DECIDE   which part of the DAG has to be "
        "repartitioned (the affected region A) and where its "
        "tasks go (pi' on surviving nodes)",
        0.8, 2.4, 11.7, 0.9, PALE, NAVY, 15)
callout(s, "SUBJECT TO   completed tasks never restart; "
        "healthy placements never move; the deadline still "
        "holds", 0.8, 3.45, 11.7, 0.9, PALE, GREY, 15)
callout(s, "MINIMIZE   the recovery cost: added makespan + "
        "tasks moved + data re-shipped, while keeping the "
        "accuracy", 0.8, 4.5, 11.7, 0.9, PALE, GOLD, 15,
        bold=True)
bullets(s, [
    (0, "Two granularity shifts at once: a task retry "
        "becomes a resource loss, and whole-DAG placement "
        "becomes minimal-region repair"),
], top=5.7, width=12.0, size=15)

# ==================================================================
# SECTION 4 — COMPLETED WORK & PRELIMINARY RESULTS
# ==================================================================
divider("4  |  COMPLETED WORK & PRELIMINARY RESULTS",
        "The platform the proposal builds on",
        "Paper 1 (published) and Paper 2 (in revision): the "
        "formulation, the schedulers, and what the data shows",
        TEAL, notes=(
    "Section four. The completed work as preliminary results: "
    "the published Cloud Summit study, then the current "
    "data-aware paper. I will show the formulation, the "
    "correctness argument, the four schedulers, the "
    "experimental setup, and then the five experiments, each "
    "with its take-away."))

s = add_slide("Paper 1: the published foundation", TEAL, S4,
              notes=(
    "IEEE Cloud Summit 2025. It established the model, "
    "placement coupled with data movement, an MILP with "
    "correctness proofs, and three scalable schedulers built "
    "around it."))
bullets(s, [
    (0, "Published at IEEE Cloud Summit 2025: 'Towards "
        "efficient allocation of tasks in DAG-based workflows "
        "across federated fog systems'"),
    (0, "Its contribution was the model plus four ways to "
        "solve it:"),
    (1, "an exact MILP with correctness proofs"),
    (1, "an LP relaxation with randomized rounding"),
    (1, "a data-aware greedy scheduler"),
    (1, "a genetic algorithm over assignments and fractions"),
    (0, "What it left open: no bound to score against, no "
        "link-degradation study, and no resource-level "
        "failures"),
], width=12.0)

s = add_slide("Paper 2: the formulation, written out", TEAL, S4,
              notes=(
    "Here is the MILP itself. The communication cost is "
    "piecewise: D over B when the edge crosses nodes, zero "
    "when the tasks are co-located. Each task gets one eligible "
    "node; a task waits for its predecessors to finish and for "
    "their data to arrive; everything finishes by the "
    "deadline; the objective is mean accuracy."))
bullets(s, [
    (0, "Communication cost:  c_ji = D_ji / B_ba when the "
        "edge crosses nodes, and 0 when the tasks are "
        "co-located"),
    (0, "Objective:  maximize  A_bar = (1/n) sum_i A_i l_i"),
    (0, "Each task goes to exactly one eligible node"),
    (0, "A task waits for every predecessor to finish AND "
        "for its data to arrive"),
    (0, "Everything finishes by t_max"),
    (0, "The e*M and e*l products are bilinear, which is "
        "what the next slide is about"),
], width=12.0, size=17)

s = add_slide("Correctness: the linearization and the proofs",
              TEAL, S4, notes=(
    "Two technical details worth your attention. First, the "
    "product e times M is linearized with a big-M helper "
    "variable z. The subtle constraint is z at least zero: "
    "without it, an unassigned node could push z negative and "
    "fake an early completion time. Second, five lemmas chain "
    "from a unique assignment up to deadline feasibility, and "
    "the theorem follows."))
bullets(s, [
    (0, "The product e*M is linearized with a helper "
        "z = e * M under big-M constraints"),
    (1, "the subtle one is z >= 0: without it, an "
        "unassigned node could push z negative and fake an "
        "early completion time"),
    (0, "Five lemmas: the assignment is unique, one positive "
        "fraction per task, the fraction lives only on the "
        "assigned node, precedence is respected, the "
        "deadline holds"),
    (0, "The theorem then says the MILP optimum is the "
        "maximum-accuracy feasible schedule"),
], width=12.0, size=17)

s = add_slide("Four schedulers, one cost model", TEAL, S4,
              notes=(
    "Every method prices transfers the same way, so the "
    "differences are algorithmic, not accounting. The MILP is "
    "the reference. LP rounding samples each task's node from "
    "the fractional solution and then re-solves the fractions. "
    "The greedy places ready tasks by earliest finish and "
    "retries with a smaller fraction when the deadline is "
    "missed. The GA searches assignments and fractions "
    "together."))
pic(s, "scheduling-pipeline.png", 0.7, 1.3, width=6.6)
bullets(s, [
    (0, "The MILP is the benchmark"),
    (0, "LP rounding relaxes, samples a node per task, "
        "re-solves the fractions"),
    (0, "The greedy places ready tasks by earliest finish; "
        "on a deadline miss it lowers the global fraction "
        "and retries"),
    (0, "The GA searches assignments and fractions as one "
        "chromosome"),
], left=7.6, width=5.2, top=1.4, size=16)

s = add_slide("Experimental setup", TEAL, S4, notes=(
    "The setup before the results. A discrete-event simulator "
    "in NumPy with SciPy HiGHS. The parameters are chosen so "
    "a transfer can genuinely rival a task, which is the "
    "regime that matters. Four datasets, five sweeps, five "
    "fresh instances per point, and the score is measured "
    "against a max-accuracy bound."))
table(s, [
    ["Component", "Setting"],
    ["Simulator", "discrete-event, Python/NumPy + SciPy HiGHS"],
    ["Task exec time t", "uniform [1, 5]"],
    ["Edge data D", "uniform [5, 50]"],
    ["Link bandwidth B", "uniform [10, 100]  "
     "(a transfer can rival a task)"],
    ["Datasets (tasks/nodes)", "10/3, 100/5, 500/8, 1000/10"],
    ["Eligibility", "~15% of placements infeasible"],
    ["Sweeps", "slack 1.0-2.0 | nodes 2-10 | tasks 10-1000 | "
     "failure 0-0.5 | bandwidth 1.0-0.05"],
    ["Metric", "mean accuracy vs the max-accuracy bound; "
     "feasibility; wall time"],
    ["Replication", "5 fresh instances per point; means reported"],
], 0.8, 1.2, 11.7, 5.5, col_widths=[3.2, 8.5], size=13)

s = add_slide("Deadline slack: the scheduler matters exactly "
              "when it hurts", TEAL, S4, notes=(
    "When the deadline barely fits, the MILP leads and "
    "everything else trails. Once there is a little slack the "
    "greedy reaches the bound, and by alpha 1.5 the MILP "
    "joins it. So the method choice matters exactly where "
    "the deadline binds; at loose slack almost anything "
    "works."))
pic(s, "perf_slack_accuracy.png", 0.7, 1.2, width=6.7)
bullets(s, [
    (0, "At alpha = 1.0 the MILP leads at 1.38 against a "
        "bound of 1.43; rounding 1.25, greedy 1.23, GA "
        "1.20"),
    (0, "From alpha = 1.2 the greedy reaches the bound; "
        "the MILP joins it at 1.5"),
    (0, "Rounding and the GA still trail 2.5 to 8 percent "
        "at alpha = 2.0; a fixed search budget cannot "
        "fully recover"),
], left=7.7, width=5.1, top=1.4, size=15)
takeaway(s, "the method choice matters most exactly where the "
         "deadline binds; at loose slack almost anything works")

s = add_slide("Federation size: capacity buys feasibility, "
              "not accuracy", TEAL, S4, notes=(
    "Scaling the federation from two to ten nodes: the MILP "
    "and the greedy sit on the bound at every size. The GA "
    "and rounding drift further below as the placement space "
    "grows while their search budget stays fixed. Extra "
    "nodes buy feasible placements, not better scores."))
pic(s, "perf_nodes_accuracy.png", 0.7, 1.2, width=6.7)
bullets(s, [
    (0, "The MILP and the greedy match the bound at every "
        "federation size"),
    (0, "The GA drifts from 1.5% below the bound at N = 2 "
        "to about 8% at N = 10; rounding behaves the same "
        "way"),
    (0, "The reason is that the placement space grows with "
        "N while the search budget stays fixed"),
], left=7.7, width=5.1, top=1.4, size=15)
takeaway(s, "federation buys feasibility, not accuracy; extra "
         "nodes never lift a method above the bound")

s = add_slide("Workflow size: the simple greedy holds up best",
              TEAL, S4, notes=(
    "Scaling the DAG: everyone is on the bound at ten tasks; "
    "at a thousand, only the greedy is still there, in a "
    "fifth of a second. Rounding survives but pays about "
    "ninety seconds per re-solve, and the GA falls to 1.10 "
    "while taking 159 seconds."))
pic(s, "perf_task_size_accuracy.png", 0.7, 1.2, width=6.7)
bullets(s, [
    (0, "At n = 10 all four methods sit on the bound"),
    (0, "At n = 100 the GA drifts first"),
    (0, "At n = 1000 the MILP is past its cap; the greedy "
        "stays on the bound in 0.15 s; rounding needs ~93 s "
        "per re-solve; the GA falls to 1.10 in ~159 s"),
], left=7.7, width=5.1, top=1.4, size=15)
takeaway(s, "at a thousand tasks only the greedy is both fast "
         "and bound-level; that result surprised us too")

s = add_slide("Failures: the scores stay flat; feasibility is "
              "the story", TEAL, S4, notes=(
    "The failure model is retry-once: a failed task reruns in "
    "place and keeps its accuracy if the retry still meets "
    "the deadline. The scores are flat for everyone; "
    "feasibility is where they separate. The greedy stays "
    "feasible at every rate because it finishes early and "
    "leaves room for the retry."))
pic(s, "perf_failure_accuracy.png", 0.7, 1.2, width=6.7)
bullets(s, [
    (0, "Retry-once: a failed task reruns in place and "
        "keeps its accuracy if the retry still meets the "
        "deadline"),
    (0, "The scores stay flat for everyone; feasibility is "
        "where they separate"),
    (0, "At failure rate 0.5: greedy 100%, MILP and GA "
        "around 60%, rounding around 20%"),
    (0, "The greedy finishes early, so a retry fits inside "
        "the deadline"),
], left=7.7, width=5.1, top=1.4, size=15)
takeaway(s, "under failures the differentiator is feasibility, "
         "not accuracy; early-finish headroom absorbs the "
         "retries")

s = add_slide("Link degradation: what data-awareness is "
              "worth", TEAL, S4, notes=(
    "This is the experiment the model was built for. Degrade "
    "every link down to five percent of nominal. The "
    "bandwidth-blind baseline reports bound-level scores at "
    "every level while its schedules go infeasible. The "
    "data-aware methods trade accuracy for feasibility and "
    "degrade gracefully."))
pic(s, "perf_bandwidth_accuracy.png", 0.7, 1.2, width=6.7)
bullets(s, [
    (0, "The blind baseline shows bound-level scores at "
        "every level, but it is infeasible: 80% at 0.5x, "
        "0% below 0.2x"),
    (0, "The MILP stays feasible at all levels and loses "
        "about 10% of score at 0.05x"),
    (0, "The greedy stays feasible to 0.1x by paying in "
        "accuracy; it collapses at 0.05x"),
    (0, "The GA holds to 0.1x; rounding only survives "
        "above 0.5x"),
], left=7.7, width=5.1, top=1.4, size=15)
takeaway(s, "a scheduler that ignores the links reports a "
         "perfect score on a workflow that finishes late; a "
         "high score that is late is a missed alert, not a "
         "result")

s = add_slide("The same story across the four datasets", TEAL,
              S4, notes=(
    "The per-dataset table says the same thing. On the small "
    "instance everyone ties and the greedy is fastest. On "
    "medium, the greedy's makespan is 43 versus about 61 for "
    "the rest. On the large instances only the greedy and the "
    "GA even fit, and the greedy holds the bound while the "
    "GA pays twenty to seventy seconds of search."))
table(s, [
    ["Dataset", "Method", "Score", "Makespan", "Runtime"],
    ["small (10/3)", "all four", "1.64", "16.8-18.9",
     "0.0001-0.27 s"],
    ["medium (100/5)", "MILP / greedy", "1.44", "61 / 43",
     "1.37 s / 0.003 s"],
    ["medium (100/5)", "rounding / GA", "1.32 / 1.27",
     "62 / 61", "24.8 s / 5.2 s"],
    ["large (500/8)", "greedy / GA", "1.42 / 1.17", "50 / 71",
     "0.04 s / 21.4 s"],
    ["xlarge (1000/10)", "greedy / GA", "1.41 / 1.13",
     "83 / 120", "0.14 s / 73.0 s"],
], 0.9, 1.4, 11.5, 3.6, col_widths=[3.0, 2.6, 1.7, 2.2, 2.0],
    size=14)
takeaway(s, "accuracy is not free in wall time, and neither "
         "is the makespan; the gap widens with scale")

s = add_slide("Structural scale: generation to a million "
              "vertices", TEAL, S4, notes=(
    "Separately we stress-tested the generators: "
    "million-task DAGs in about three seconds with depth "
    "growing like log n, and million-node resource graphs in "
    "about seven. These are structural instances; the honest "
    "boundary is that schedulable dense instances stop where "
    "the constraint count and memory do."))
bullets(s, [
    (0, "The DAG generator makes 10^6 tasks, about 3 "
        "million edges, in 3.1 s; depth grows like log n"),
    (0, "Resource graphs: 10^6 nodes, about 2.4 million "
        "links, in 7.3 s; average degree around 5"),
    (0, "These are structural instances; schedulable dense "
        "instances stop where the constraints do"),
    (1, "MILP near 800 assignment variables; the LP near "
        "10^5 rows at n = 1000"),
], width=6.9, size=16)
pic(s, "resource_graphs.png", 7.6, 1.35, width=5.4, base=RES)
caption(s, "Generated federated resource graphs (up to 10^6 "
           "nodes)", 7.6, 6.55, 5.4)

s = add_slide("Honest limits, and what they leave open", TEAL,
              S4, notes=(
    "What we do not claim: the MILP is capped near 800 "
    "variables, the LP grows to a hundred thousand rows, the "
    "GA runs on one budget, and the failure model is "
    "retry-once-in-place. No replication, no checkpointing, "
    "no migration. That last limit is the bridge to the "
    "proposal."))
bullets(s, [
    (0, "The MILP is capped at about 800 assignment "
        "variables; that is a deliberate boundary, not an "
        "oversight"),
    (0, "The LP reaches ~10^5 rows at n = 1000, and the GA "
        "runs on one fixed budget"),
    (0, "The failure model is retry-once-in-place: no "
        "replication, checkpointing, or migration yet"),
    (0, "Dense schedulable instances stop near 10^4 "
        "tasks; the 10^6 experiments are structural"),
    (0, ""),
    (0, "What is open: a whole resource fails mid-workflow, "
        "and the schedule was decided up front"),
], width=12.0, size=16)

# ==================================================================
# SECTION 5 — PROPOSED RESEARCH
# ==================================================================
divider("5  |  PROPOSED RESEARCH",
        "Dynamic Partial Repartitioning",
        "Repair the smallest affected region and leave "
        "everything else alone", AMBER, notes=(
    "Section five is the proposal itself. The question in one "
    "line, the three research questions, and then the method "
    "in depth."))

s = add_slide("The proposal, and the questions it raises",
              AMBER, S5, notes=(
    "The proposal in one line, then the three research "
    "questions that decompose it: where the repair boundary "
    "lies, how to repartition that region, and how to update "
    "the paths without recomputing them."))
callout(s, "How can we quickly repartition and reschedule "
        "only the affected part of a DAG workflow after a fog "
        "resource fails, while reducing recovery time, "
        "communication cost, task movement, and completion "
        "time?", 0.8, 1.3, 11.7, 1.1, PALE, AMBER, 15,
        bold=True)
bullets(s, [
    (0, "RQ1, the boundary: what is the smallest DAG region "
        "that must be repartitioned?"),
    (0, "RQ2, the repair: how do we repartition that region "
        "onto surviving nodes at minimum recovery cost and "
        "still meet the deadline?"),
    (0, "RQ3, the paths: how do we update communication "
        "paths incrementally instead of recomputing them?"),
], top=2.9, width=12.0, size=17)

s = add_slide("A resource fails mid-workflow", AMBER, S5,
              notes=(
    "Monitoring detects the failed node. The stranded, "
    "unfinished tasks have to be rescued, and completed work "
    "is never redone. The subtle decision is the boundary: "
    "we check the parents and children of the stranded "
    "tasks, because sometimes a dependent has to move too, "
    "for data locality or to make the deadline."))
for base_x, title, dead in [(0.9, "before", None),
                            (8.0, "after R2 fails", "R2")]:
    box(s, title, base_x, 1.35, 4.3, 0.5, NAVY, size=13,
        bold=True)
    pos = {"R1": (base_x + 0.1, 2.15), "R2": (base_x + 1.75, 1.95),
           "R3": (base_x + 1.75, 3.35), "R4": (base_x + 3.45, 2.6)}
    for name, (x, y) in pos.items():
        c = PALE if name != dead else GREY
        tc = NAVY if name != dead else WHITE
        box(s, name, x, y, 0.85, 0.6, c, text_color=tc, size=12,
            bold=True)
    arrow(s, base_x + 0.95, 2.45, base_x + 1.75, 2.25, GREY, 1.5)
    arrow(s, base_x + 0.95, 2.45, base_x + 1.75, 3.65, GREY, 1.5)
    arrow(s, base_x + 2.6, 2.25, base_x + 3.45, 2.9, GREY, 1.5)
    arrow(s, base_x + 2.6, 3.65, base_x + 3.45, 3.1, GREY, 1.5)
    if dead:
        cross(s, base_x + 1.75, 1.95, 0.85)
        box(s, "stranded tasks", base_x + 0.5, 4.35, 3.3, 0.55,
            AMBER, size=12, bold=True)
        arrow(s, base_x + 2.15, 4.35, base_x + 2.15, 2.6, AMBER,
              1.75, dashed=True)
bullets(s, [
    (0, "The invariant: completed tasks never restart, and "
        "healthy tasks never move"),
    (0, "The boundary question (RQ1): is rescuing just the "
        "stranded tasks enough, or do dependents have to "
        "move too?"),
], top=5.3, width=12.0, size=16)

s = add_slide("The method, step by step", AMBER, S5, notes=(
    "Seven steps. The existing schedulers make the initial "
    "partition. When a failure is detected we isolate the "
    "stranded tasks, grow the minimal affected subgraph under "
    "the boundary rule, pick replacements by capacity and "
    "short paths to the parents and children, repartition "
    "under the recovery cost model, assign and update only "
    "the affected paths, and resume from the last good "
    "point."))
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
    box(s, num, x, 1.5, 1.55, 0.55, c, size=16, bold=True)
    box(s, txt, x, 2.15, 1.55, 1.15, PALE, text_color=DARK,
        size=12)
    if i:
        arrow(s, x - 0.25, 2.7, x, 2.7, GREY, 2.0)
callout(s, "The repartition cost model: added makespan, "
        "communication delay, data re-shipped, move cost, "
        "load balance, all under the deadline",
        0.9, 3.8, 11.5, 0.9, PALE, AMBER, 15)
callout(s, "And one invariant throughout: completed tasks "
        "never restart, and unaffected assignments never "
        "move.", 0.9, 4.9, 11.5, 0.8, PALE, NAVY, 15)

s = add_slide("RQ1: where does the repair boundary lie?",
              AMBER, S5, notes=(
    "The technical heart of the proposal. The stranded set "
    "S is mandatory. But some neighbors have to move too: a "
    "child whose input now crosses a long path, or a "
    "dependent that can no longer meet the deadline if it "
    "stays. The rule expands from S while a neighbor fails "
    "a stay-test, capped so the region stays small."))
bullets(s, [
    (0, "Start with the stranded set S; that part is "
        "mandatory"),
    (0, "Then admit a neighbor while it fails one of two "
        "stay-tests:"),
    (1, "a deadline test: staying pushes its finish time "
        "past the slack remaining at tau"),
    (1, "a locality test: staying strands its input on a "
        "path too slow to serve it in time"),
    (0, "Stop when no neighbor fails a test, or when the "
        "region hits a size cap; minimality is the claim "
        "we verify"),
    (0, "The output is the affected subgraph plus its "
        "boundary pins: the tasks that stayed put and fix "
        "the arrival times the repair must respect"),
], width=12.0, size=16)

s = add_slide("RQ2: repartitioning the region", AMBER, S5,
              notes=(
    "The repair itself is a smaller instance of the same "
    "optimization family, which is the point: the paper-two "
    "schedulers become the region solvers. The recovery "
    "objective adds movement terms to the accuracy "
    "objective, and the boundary pins enter as fixed "
    "arrival times the repair has to respect."))
bullets(s, [
    (0, "Repair is a constrained re-optimization on the "
        "region; the paper-two schedulers become the "
        "region solvers"),
    (0, "The objective minimizes added makespan plus moved "
        "tasks plus re-shipped data, subject to accuracy "
        "and the deadline"),
    (0, "The boundary pins enter as constants: the arrival "
        "times of data from tasks that stayed put"),
    (0, "Replacement resources come from the surviving "
        "nodes with enough capacity and short paths to "
        "where the parents and children live"),
    (0, "A greedy repair gives millisecond-scale answers; "
        "the MILP repair is the reference for small "
        "regions"),
], width=12.0, size=16)

s = add_slide("RQ3: updating the paths incrementally", AMBER,
              S5, notes=(
    "Moved tasks need new paths to their parents and "
    "children. Recomputing all shortest paths mid-workflow "
    "is too slow, so we reuse the dynamic SPT updates from "
    "Riazi, Khanda and Bhowmick: only the paths through the "
    "deleted node and the moved tasks get updated. That is "
    "what makes partial repair fast enough to matter."))
bullets(s, [
    (0, "Moved tasks need new communication paths to "
        "their parents and children"),
    (0, "Recomputing all shortest paths on the "
        "infrastructure graph mid-workflow is too slow"),
    (0, "So we reuse dynamic single-source shortest-path "
        "updates (Riazi, Khanda, Bhowmick and "
        "colleagues)"),
    (1, "only the paths through the deleted node and the "
        "moved tasks get updated"),
    (0, "Using dynamic SPT to drive workflow recovery is, "
        "as far as we know, new"),
], width=12.0, size=16)

s = add_slide("What is new, positioned against the "
              "literature", AMBER, S5, notes=(
    "The pieces exist separately: dynamic path updates, fog "
    "rescheduling, join-leave redistribution, partial "
    "reconsideration. Nobody couples them. The novelty is "
    "the two-graph mapping: a failure in the "
    "infrastructure becomes the smallest affected region "
    "in the task DAG."))
bullets(s, [
    (0, "Dynamic shortest-path updates exist, but have "
        "never driven workflow repartitioning"),
    (0, "Fog rescheduling and join-leave redistribution "
        "exist, but without the two-graph coupling"),
    (0, "Partial workflow reconsideration exists, but "
        "not at failure granularity"),
    (0, ""),
    (0, "What is new: an infrastructure-node failure "
        "maps to the smallest affected DAG region; only "
        "that region is repartitioned; the paths update "
        "incrementally; the workflow resumes"),
], width=12.0, size=16)

# ==================================================================
# SECTION 6 — EVALUATION PLAN & TIMELINE
# ==================================================================
divider("6  |  EVALUATION PLAN & TIMELINE",
        "How it will be tested, and when",
        "Baselines, metrics, failure injection, hypotheses, "
        "milestones", AMBER, notes=(
    "Section six. The evaluation design, then the "
    "twelve-month plan."))

s = add_slide("Baselines and metrics", AMBER, S6, notes=(
    "Four baselines: complete repartition as the naive "
    "upper bound on disturbance, a greedy rescue as the "
    "cheapest possible repair, a no-repair static baseline "
    "as the quality floor, and the MILP on small cases as "
    "the reference. The metrics cover recovery speed, "
    "schedule quality, and the cost of the disturbance."))
table(s, [
    ["Baselines", "Metrics"],
    ["Complete repartition: reschedule the whole DAG",
     "Recovery time (detect to resume)"],
    ["Greedy rescue: reassign stranded tasks one by one",
     "Completion time / deadline success rate"],
    ["Static, no repair: whatever survives",
     "Communication cost and data re-shipped"],
    ["MILP repair on small cases: the reference",
     "Tasks moved; energy; repaired-schedule quality"],
], 0.8, 1.4, 11.7, 3.4, col_widths=[6.2, 5.5], size=13)
takeaway(s, "the platform from paper two already supplies "
         "the baselines and the failure injection; the "
         "testbed exists", accent=TEAL)

s = add_slide("Experiment design, and the hypotheses", AMBER,
              S6, notes=(
    "We vary what makes recovery hard: where the failure "
    "hits, how many resources fail at once, how much slack "
    "remains, and the scales. The interesting case is a "
    "late failure on the critical path. Three hypotheses, "
    "each falsifiable."))
bullets(s, [
    (0, "Failure injection:"),
    (1, "where it hits: a resource on the critical path "
        "versus a peripheral one"),
    (1, "how many: a single resource versus several at "
        "once"),
    (1, "when: how much deadline slack remains at tau"),
    (0, "Scale: workflows of 10, 100 and 1000 tasks, "
        "federations of 2 to 10 nodes"),
    (0, "Hypotheses:"),
    (1, "H1: recovery time grows with the size of the "
        "region, not the size of the DAG"),
    (1, "H2: tasks moved and data re-shipped are far "
        "below the baselines at equal feasibility"),
    (1, "H3: repair quality stays within a small margin "
        "of the MILP reference on small cases"),
], width=12.0, size=16)

s = add_slide("Timeline: twelve months", AMBER, S6, notes=(
    "Four quarters: build, solve, evaluate, write. The "
    "deliverables land on the existing public repository "
    "and the paper targets the systems venues."))
table(s, [
    ["Months", "Milestone", "Deliverable"],
    ["1-3", "Extend the simulator to resource failures; "
     "boundary rule and affected-subgraph extraction; "
     "complete-repartition baseline",
     "RQ1 implemented; baseline working"],
    ["4-6", "Repartition algorithm and replacement "
     "selection; incremental SPT update",
     "RQ2 and RQ3 implemented"],
    ["7-9", "Full baseline comparison; MILP reference on "
     "small cases; boundary-rule sensitivity",
     "H1-H3 tested"],
    ["10-12", "Write the paper; release the code on the "
     "public repository; submit",
     "Paper and artifact"],
], 0.8, 1.4, 11.7, 4.4, col_widths=[1.4, 7.0, 3.3], size=13)

s = add_slide("Risks, and how I plan to handle them", AMBER,
              S6, notes=(
    "Three honest risks. The boundary rule might expand "
    "to most of the DAG; the incremental SPT might not "
    "pay off on small graphs; the region repair might "
    "trail the MILP quality. Each has a mitigation built "
    "into the plan."))
bullets(s, [
    (0, "The boundary rule might degenerate into "
        "'repartition everything'"),
    (1, "so the cap on the region size is enforced, and "
        "the sensitivity study measures it against "
        "failure location and slack"),
    (0, "Incremental SPT might not pay off on small "
        "graphs"),
    (1, "so we measure the break-even point and keep "
        "full recomputation as a baseline"),
    (0, "Region repair might trail the MILP quality"),
    (1, "so the strategy is hybrid: greedy repair at "
        "scale, MILP repair where the region is small"),
], width=12.0, size=16)

# ==================================================================
# SECTION 7 — CONCLUSION
# ==================================================================
s = add_slide("Conclusion: what this research contributes",
              NAVY, S7, notes=(
    "To conclude. The completed work gives a proved, "
    "data-aware formulation, four schedulers on one cost "
    "model, and a reproducible platform. The proposal "
    "adds three contributions: a principled boundary "
    "rule, a minimal-region repartitioning method, and "
    "the first use of incremental path updates for "
    "workflow recovery."))
bullets(s, [
    (0, "Already done: a proved, data-aware "
        "formulation, four schedulers on one cost "
        "model, and a reproducible platform"),
    (0, "Proposed contribution 1: a principled "
        "boundary rule for the smallest affected DAG "
        "region (RQ1)"),
    (0, "Proposed contribution 2: minimal-region "
        "repartitioning under a recovery cost model "
        "(RQ2)"),
    (0, "Proposed contribution 3: incremental path "
        "updates for workflow recovery (RQ3)"),
    (0, "Expected outcome: recovery that is faster "
        "and less disturbing than a complete "
        "repartition, at near-reference quality"),
    (0, ""),
    (0, "Paper 1 placed the workflow; Paper 2 "
        "priced its data and its approximation; "
        "Paper 3 keeps it alive when the "
        "infrastructure fails."),
], width=12.0, size=17)

# ---- closing ----
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
