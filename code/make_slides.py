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
NAVY   = RGBColor(0x0B, 0x2A, 0x4A)   # deep navy  — headers, dividers
TEAL   = RGBColor(0x0E, 0x7C, 0x7B)   # teal       — completed work
AMBER  = RGBColor(0xC7, 0x5B, 0x12)   # amber      — proposed work
GOLD   = RGBColor(0xE0, 0xA4, 0x1E)   # gold       — accents
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
        _footer(s, part)
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
            accent=TEAL, size=15, bold=False, text_color=DARK):
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
    p.font.size = Pt(size); p.font.bold = bold
    p.font.color.rgb = text_color


def takeaway(slide, text, left=0.7, top=5.95, width=11.9, height=0.95,
             accent=GOLD):
    """Amber 'take-away' box pinned to the bottom of a results slide."""
    callout(slide, "Take-away:  " + text, left, top, width, height,
            PALE, accent, 14, bold=False)


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
    lnEl = ln.line._get_or_add_ln()
    from pptx.oxml.ns import qn
    he = lnEl.makeelement(qn('a:headEnd'), {'type': 'none'})
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
    box_ = slide.shapes.add_textbox(Inches(left), Inches(top),
                                    Inches(width), Inches(0.6))
    p = box_.text_frame.paragraphs[0]
    p.text = text
    p.font.size = Pt(11)
    p.font.italic = True
    p.font.color.rgb = GREY
    p.alignment = PP_ALIGN.CENTER


def table(slide, rows, l, t, w, h, col_widths=None, size=12,
          header_fill=NAVY, header_color=WHITE, body_fill=WHITE):
    """Add a table; rows[0] is treated as the header row."""
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
            p.font.size = Pt(size if ri else size)
            p.font.bold = ri == 0
            p.font.color.rgb = header_color if ri == 0 else DARK
    return tbl


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
     ("Advisor: Mohsen Amini Salehi", 15),
     ("github.com/gayanigupta/data-aware-scheduling", 13)],
    NAVY,
    notes=("Welcome. This is my PhD research proposal. The talk "
           "follows the standard structure: motivation, related "
           "work and the gap, a formal problem definition, the work "
           "already completed and its evidence, the proposed "
           "research, the evaluation plan and timeline, and a "
           "conclusion."))

s = add_slide("Outline", NAVY, "", notes=(
    "Seven sections. Sections 1-3 set up the problem. Section 4 "
    "reports completed work — the published Cloud Summit paper and "
    "the current data-aware study — as preliminary results. "
    "Sections 5-6 are the proposal itself. Section 7 concludes."))
for i, txt in enumerate([
        "1   Introduction & motivation",
        "2   Related work — and the gap",
        "3   Problem definition",
        "4   Completed work & preliminary results",
        "5   Proposed research — dynamic partial repartitioning",
        "6   Evaluation plan & timeline",
        "7   Conclusion — expected contributions"]):
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
        "Time-critical workflows, unreliable networks, and the case "
        "for the federated fog", NAVY, notes=(
    "Section 1. The motivation in one paragraph: time-critical "
    "workflows must run when the network is at its worst, and "
    "nearby fog machines — federated — are the only capacity left."))

s = add_slide("The scenario", NAVY, S1, notes=(
    "A river basin floods. The response workflow — sense, model, "
    "forecast, plan, alert — runs as a DAG. The deadline is hard: "
    "a forecast after the water is useless. And the uplink to the "
    "cloud is degraded or gone — the same event that creates the "
    "deadline also takes away the network."))
bullets(s, [
    (0, "A disaster unfolds: flood, wildfire, offshore incident"),
    (0, "The deadline is hard: a forecast that arrives late is a "
        "forecast nobody uses"),
    (0, "The uplink to the cloud is degraded or gone — the work "
        "must run on nearby fog machines"),
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

s = add_slide("Federation is the answer — with a scheduling price",
              NAVY, S1, notes=(
    "One fog site is rarely enough. Nearby sites keep fast links "
    "to each other even when the cloud link dies, so federating "
    "them creates a small local cloud. The price: every task now "
    "has a placement choice, and every choice ships data across a "
    "link."))
bullets(s, [
    (0, "Fog sites near the event: cell-tower racks, roadside "
        "cabinets, platform servers"),
    (0, "Individually too weak — but they keep fast, stable links "
        "to each other even when the cloud link fails"),
    (0, "Federation = a small local cloud built from nearby "
        "sites"),
    (0, "The price: every task can run in many places, and "
        "wherever it runs, its input data has to get there first"),
], width=6.9)
pic(s, "federated-fog-architecture.png", 7.7, 1.35, width=5.2)
caption(s, "Federated fog deployment around a disaster area",
        7.7, 6.45, 5.2)

s = add_slide("Two interacting decisions", NAVY, S1, notes=(
    "Two levers define this problem. Lever one: data movement — "
    "transfer time D over B can rival a task's own runtime, so the "
    "'fastest' node can be the worst once you pay to move the "
    "input. Lever two: approximate execution — a fraction of the "
    "work costs that fraction of the time and returns that "
    "fraction of the accuracy. The levers interact: placement "
    "decides transfers, fractions decide runtimes."))
bullets(s, [
    (0, "Lever 1 — data movement"),
    (1, "every edge carries D_ji across a link of bandwidth B"),
    (1, "transfer time D_ji/B can rival the task's own runtime"),
    (0, "Lever 2 — approximate execution"),
    (1, "run fraction l of a task -> l of the time, l of the "
        "accuracy"),
    (1, "a flood model at 80% fidelity still warns in time"),
    (0, "The levers interact: placement decides transfers; "
        "fractions decide runtimes"),
], width=12.0)

s = add_slide("The dissertation as three papers", NAVY, S1,
              notes=(
    "The whole PhD is three papers on one arc. Paper 1 — "
    "published at Cloud Summit 2025 — built the model and four "
    "schedulers. Paper 2 — the current submission — hardened it: "
    "data-aware, bounded, stress-tested. Paper 3 — this proposal "
    "— repairs the smallest affected region when a whole "
    "resource fails. Each paper answers the question the "
    "previous one left open."))
for i, (k, txt, c) in enumerate([
    ("PAPER 1", "Efficient DAG task allocation across federated "
     "fog — the model + 4 schedulers.  Published: IEEE Cloud "
     "Summit 2025", TEAL),
    ("PAPER 2", "Data-aware scheduling of approximate DAG "
     "workflows — bound, retry semantics, bandwidth "
     "degradation, scale limits.  Submitted: CCGrid 2027",
     TEAL),
    ("PAPER 3", "Dynamic partial repartitioning after resource "
     "failure — minimal-region repair, incremental paths.  "
     "This proposal — target: IPDPS / CCGrid 2028", AMBER)]):
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
divider("2  |  RELATED WORK", "What is known — and what is missing",
        "Four research threads converge; none covers the whole "
        "problem", NAVY, notes=(
    "Section 2. Related work in four threads: classic DAG "
    "scheduling, fog/edge placement, approximate computing, and "
    "failure recovery / rescheduling. Then the gap in one table."))

s = add_slide("Thread 1 — DAG scheduling & placement", NAVY, S2,
              notes=(
    "HEFT is the reference point: rank tasks by upward rank, "
    "place each where it finishes earliest. It is compute-centric "
    "in spirit — transfers appear only as static edge weights, "
    "tasks always run completely, and the plan is fixed at "
    "submission."))
bullets(s, [
    (0, "HEFT (Topcuoglu et al. 2002) — the reference DAG "
        "scheduler"),
    (1, "upward-rank priority; earliest-finish-time placement"),
    (1, "transfers are static edge weights; full execution only"),
    (0, "CPOP, PEFT and descendants — same template, refined "
        "priorities"),
    (0, "Federated-fog variants add eligibility and federation "
        "constraints (our Paper 1 builds here)"),
    (0, "Common assumption: one static plan, decided before "
        "execution"),
], width=12.0)

s = add_slide("Thread 2 — Fog / edge scheduling", NAVY, S2, notes=(
    "Fog schedulers handle capacity, eligibility and heterogeneity "
    "across edge, fog and cloud tiers. But they treat tasks as "
    "atomic — no execution fractions — and data movement is "
    "usually a fixed cost or ignored."))
bullets(s, [
    (0, "Fog/edge schedulers manage capacity, eligibility, "
        "heterogeneity across the compute continuum"),
    (0, "Surveys (Mouradian et al. 2018) catalog placement "
        "policies for fog and edge"),
    (0, "Data-aware variants price locality — but rarely "
        "per-link bandwidth explicitly"),
    (0, "Tasks are atomic: run completely or not at all"),
    (0, "Schedules are decided up front — failures handled by "
        "restart, not repair"),
], width=12.0)

s = add_slide("Thread 3 — Approximate computing", NAVY, S2, notes=(
    "Approximate computing trades result quality for time or "
    "energy — loop truncation, reduced precision, early "
    "termination. Powerful for deadline workloads, but the "
    "literature assumes data is already where it needs to be."))
bullets(s, [
    (0, "Trades result quality for time or energy"),
    (1, "loop truncation, reduced precision, early termination"),
    (0, "Makes accuracy a schedulable resource — exactly what "
        "tight deadlines need"),
    (0, "But: the literature assumes data is already in place"),
    (1, "inter-node transfer cost is not part of the trade"),
    (0, "Ours: approximation + per-edge data + per-link "
        "bandwidth, jointly"),
], width=12.0)

s = add_slide("Thread 4 — Failure recovery & rescheduling",
              NAVY, S2, notes=(
    "The closest literature to the proposal. Rescheduling "
    "reconsiders a workflow at chosen points (Sakellariou & "
    "Zhao); fog studies redistribute tasks on join/leave or "
    "uncertain events; dynamic shortest-path algorithms update "
    "routing after a graph change. None couples an "
    "infrastructure-node failure to the smallest affected region "
    "of the task DAG."))
bullets(s, [
    (0, "Workflow rescheduling (Sakellariou & Zhao 2004): "
        "reconsider the plan at chosen points — but re-map "
        "globally"),
    (0, "Fog task redistribution on node join/leave "
        "(Lee et al. 2019); uncertain-event rescheduling "
        "(Yang et al. 2024)"),
    (0, "Checkpoint/restart and replication — recover work, "
        "at replication or recompute cost"),
    (0, "Dynamic shortest-path updates (Riazi, Bhowmick, "
        "Khanda et al.) — repair routing after graph change; "
        "never applied to workflow repartitioning"),
    (0, "Nobody couples: infra-node failure -> smallest "
        "affected DAG region -> repartition only that"),
], width=12.0)

s = add_slide("The gap, in one table", NAVY, S2, notes=(
    "Read each column as a capability. Classic schedulers place "
    "but neither price data per-link nor approximate nor repair. "
    "Fog schedulers add data-awareness. Our Paper 2 adds "
    "approximation. The last column — repairing only the affected "
    "region after a resource failure — is empty. That is the "
    "proposal."))
table(s, [
    ["Capability", "HEFT / classic", "Fog schedulers",
     "Paper 1 + 2 (ours)", "Proposed work"],
    ["Placement on heterogeneous nodes", "yes", "yes", "yes",
     "yes"],
    ["Per-edge data + per-link bandwidth", "no", "partial",
     "yes", "yes"],
    ["Approximate execution fractions", "no", "no", "yes", "yes"],
    ["Recovery after resource failure", "restart",
     "reschedule all", "retry task", "repair region only"],
], 0.8, 1.35, 11.7, 3.4,
    col_widths=[4.3, 1.85, 1.85, 1.85, 1.85], size=13)
callout(s, "Gap: no method couples an infrastructure-node "
        "failure to the smallest affected region of the task DAG.",
        0.8, 5.3, 11.7, 0.95, PALE, AMBER, 15, bold=True)

# ==================================================================
# SECTION 3 — PROBLEM DEFINITION
# ==================================================================
divider("3  |  PROBLEM DEFINITION", "The problem, stated precisely",
        "Two graphs, one coupling, a hard deadline", NAVY, notes=(
    "Section 3. Before any algorithm: the system model and the "
    "formal problem statement — the same notation the MILP in "
    "Section 4 uses."))

s = add_slide("System model — two graphs", NAVY, S3, notes=(
    "The task graph: nodes T_i, edges carry D_ji bytes of "
    "dependency data. The infrastructure graph: fog nodes f_a "
    "with capacity and eligibility, links (b,a) with bandwidth "
    "B_ba. The partition maps tasks to nodes; the failure event "
    "deletes a node from one graph and strands work in the "
    "other."))
bullets(s, [
    (0, "Task graph  G_T = (T, E):  task T_i with exec time "
        "t_ia, accuracy A_i, eligibility P_ia"),
    (1, "edge (j,i) carries D_ji bytes of dependency data"),
    (0, "Infrastructure graph  G_R = (R, L):  node f_a with "
        "capacity, memory, availability"),
    (1, "link (b,a) with bandwidth B_ba and delay"),
    (0, "Partition pi: T -> R, one eligible node per task"),
    (0, "Failure event: delete a node r* from G_R -> stranded "
        "tasks in G_T"),
], width=6.9)
# drawn diagram: task DAG (left) coupled to infra graph (right)
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

s = add_slide("Problem statement — the static core", NAVY, S3,
              notes=(
    "The completed work's problem, stated formally: given the two "
    "graphs and a deadline, choose an assignment and a fraction "
    "per task, finish before the deadline, maximize average "
    "accuracy. NP-hard — even on unrelated parallel machines."))
callout(s, "GIVEN:  task DAG (exec times, data sizes, accuracies, "
        "eligibility)  +  infra graph (capacities, bandwidths)  +  "
        "deadline t_max", 0.8, 1.35, 11.7, 0.85, PALE, NAVY, 14)
callout(s, "DECIDE:  assignment e_ia in {0,1}   and   execution "
        "fraction l_ia in [0,1]   for every task i", 0.8, 2.35,
        11.7, 0.85, PALE, TEAL, 14)
callout(s, "SUBJECT TO:  one eligible node per task;  precedence "
        "+ data-arrival order;  makespan <= t_max", 0.8, 3.35,
        11.7, 0.85, PALE, GREY, 14)
callout(s, "MAXIMIZE:  average accuracy  A_bar = (1/n) "
        "sum_i A_i * l_i", 0.8, 4.35, 11.7, 0.85, PALE, GOLD, 14,
        bold=True)
bullets(s, [
    (0, "NP-hard even on unrelated parallel machines — exact "
        "solution is the benchmark, not the product"),
], top=5.55, width=12.0, size=15)

s = add_slide("Problem statement — the dynamic extension "
              "(the proposal)", NAVY, S3, notes=(
    "The proposal extends the same model with a failure event. At "
    "time tau a resource r* fails. Tasks partition into done, "
    "running, pending. Stranded = unfinished tasks on r*. The "
    "problem: find the smallest affected region A of the DAG and "
    "a repair assignment on surviving nodes that meets the "
    "deadline at minimum disturbance — done tasks never restart, "
    "unaffected assignments never move."))
callout(s, "EVENT:  at time tau, resource r* fails  ->  "
        "stranded set S = unfinished tasks on r*", 0.8, 1.35,
        11.7, 0.85, PALE, AMBER, 14)
callout(s, "DECIDE:  the affected region A (superset of S, inside "
        "G_T)  +  repair assignment pi': A -> R \\ {r*}", 0.8,
        2.35, 11.7, 0.85, PALE, NAVY, 14)
callout(s, "SUBJECT TO:  completed tasks never restart;  "
        "unaffected assignments never move;  deadline still met",
        0.8, 3.35, 11.7, 0.85, PALE, GREY, 14)
callout(s, "MINIMIZE:  recovery cost = added makespan + tasks "
        "moved + data re-shipped   while keeping accuracy",
        0.8, 4.35, 11.7, 0.85, PALE, GOLD, 14, bold=True)
bullets(s, [
    (0, "Two granularity shifts at once: task retry -> resource "
        "loss;  whole-DAG placement -> minimal-region repair"),
], top=5.55, width=12.0, size=15)

# ==================================================================
# SECTION 4 — COMPLETED WORK & PRELIMINARY RESULTS
# ==================================================================
divider("4  |  COMPLETED WORK & PRELIMINARY RESULTS",
        "The platform the proposal builds on",
        "Paper 1 (published) + Paper 2 (submitted): formulation, "
        "schedulers, and what the data shows", TEAL, notes=(
    "Section 4. Completed work as preliminary results: the "
    "published Cloud Summit study, then the current data-aware "
    "paper — formulation, correctness, schedulers, setup, five "
    "experiments each with a take-away, and the limits that "
    "motivate the proposal."))

s = add_slide("Paper 1 — the published foundation", TEAL, S4,
              notes=(
    "IEEE Cloud Summit 2025. Established the model — placement "
    "coupled with data movement — an MILP with correctness "
    "proofs, and three scalable schedulers: LP relaxation with "
    "randomized rounding, a data-aware greedy, and a genetic "
    "algorithm."))
bullets(s, [
    (0, "IEEE Cloud Summit 2025: 'Towards efficient allocation "
        "of tasks in DAG-based workflows across federated fog "
        "systems'"),
    (0, "Contribution: the model + four ways to solve it"),
    (1, "MILP — exact, with correctness proofs"),
    (1, "LP relaxation + randomized rounding"),
    (1, "data-aware greedy — priority beta*A_i + (1-beta)*CP_i"),
    (1, "genetic algorithm — assignment + fractions as one "
        "chromosome"),
    (0, "Left open: no bound, no link-degradation study, no "
        "resource-level failures"),
], width=12.0)

s = add_slide("Paper 2 — the formulation, written out", TEAL, S4,
              notes=(
    "The MILP itself. Communication delay is piecewise: D over B "
    "across nodes, zero co-located. One eligible node per task; a "
    "successor waits for finish AND data arrival; completion "
    "inside the deadline; the objective is mean accuracy."))
bullets(s, [
    (0, "Communication:  c_ji^ba = D_ji / B_ba  if b != a,  "
        "0 if co-located"),
    (0, "Objective:  max  A_bar = (1/n) sum_i A_i sum_a l_ia"),
    (0, "Placement:  sum_a e_ia = 1   over eligible nodes only"),
    (0, "Precedence + data:  M_ia >= y_j + c_ji^ba * e_jb  "
        "for all edges (j,i)"),
    (0, "Deadline:  y_i = sum_a e_ia (M_ia + t_ia l_ia) <= "
        "t_max"),
    (0, "Products e*M and e*l are bilinear -> needs "
        "linearization (next slide)"),
], width=12.0, size=16)

s = add_slide("Correctness — linearization and lemmas", TEAL, S4,
              notes=(
    "Two technical pieces worth showing. First, the products "
    "e*M are linearized with a big-M helper z; the "
    "non-obvious detail is z >= 0 — without it, unassigned "
    "nodes could push z negative and fake a feasible completion "
    "time. Second, five lemmas: uniqueness of the assignment, "
    "one fraction per task, start-time correctness, precedence "
    "correctness, then the theorem that optimality equals the "
    "best feasible schedule."))
bullets(s, [
    (0, "Linearization:  z_ia := e_ia * M_ia   via big-M"),
    (1, "z <= M_ia + t_max(1 - e);   z >= M_ia - t_max(1 - e);   "
        "z <= t_max * e;   z >= 0"),
    (1, "z >= 0 matters: without it a negative z on an "
        "unassigned node could fake an early finish"),
    (0, "Correctness chain:  L1 unique assignment -> L2 single "
        "positive fraction -> L3 l>0 only on the assigned node "
        "-> L4 precedence order -> L5 deadline feasibility"),
    (0, "Theorem:  the MILP optimum is the maximum-accuracy "
        "feasible schedule"),
], width=12.0, size=16)

s = add_slide("Four schedulers on one cost model", TEAL, S4,
              notes=(
    "Same communication-cost model under every method, so "
    "differences are algorithmic, not accounting. MILP is the "
    "reference. LP rounding samples each task's node from the "
    "fractional solution, then re-solves fractions. Greedy uses "
    "priority and earliest-finish placement with a "
    "fraction-retry. The GA searches assignments and fractions "
    "together with a co-location repair."))
pic(s, "scheduling-pipeline.png", 0.7, 1.3, width=6.6)
bullets(s, [
    (0, "MILP (HiGHS) — the benchmark"),
    (0, "LP rounding — relax, sample node per task, re-solve "
        "fractions"),
    (0, "Greedy — priority + earliest finish; deadline miss -> "
        "lower global fraction and retry"),
    (0, "GA — chromosome = assignment + fractions; fitness = "
        "accuracy - lateness penalty"),
], left=7.6, width=5.2, top=1.4, size=15)

s = add_slide("Experimental setup", TEAL, S4, notes=(
    "The setup before the results. Discrete-event simulator, "
    "NumPy + SciPy HiGHS. Parameters chosen so a transfer can "
    "genuinely rival a task — the contested regime. Four "
    "datasets, five sweeps, five fresh instances per point. "
    "Metric is average accuracy against the max-accuracy bound, "
    "plus feasibility and wall time."))
table(s, [
    ["Component", "Setting"],
    ["Simulator", "discrete-event, Python/NumPy + SciPy HiGHS"],
    ["Task exec time t", "uniform [1, 5]"],
    ["Edge data D", "uniform [5, 50]"],
    ["Link bandwidth B", "uniform [10, 100]  "
     "(transfer can rival a task)"],
    ["Datasets (tasks/nodes)", "10/3, 100/5, 500/8, 1000/10"],
    ["Eligibility", "~15% of placements infeasible"],
    ["Sweeps", "slack 1.0-2.0 | nodes 2-10 | tasks 10-1000 | "
     "failure 0-0.5 | bandwidth 1.0-0.05"],
    ["Metric", "mean accuracy vs max-accuracy bound; "
     "feasibility; wall time"],
    ["Replication", "5 fresh instances per point; means reported"],
], 0.8, 1.2, 11.7, 5.5, col_widths=[3.2, 8.5], size=12)

s = add_slide("Q1 — Deadline slack: the scheduler matters exactly "
              "when it hurts", TEAL, S4, notes=(
    "At alpha=1.0 the deadline barely fits: MILP 1.38 vs bound "
    "1.43, rounding 1.25, greedy 1.23, GA 1.20. From alpha=1.2 "
    "greedy reaches the bound; MILP joins by 1.5. Take-away: "
    "method choice matters exactly where the deadline binds; "
    "at loose slack almost anything works."))
pic(s, "perf_slack_accuracy.png", 0.7, 1.2, width=6.7)
bullets(s, [
    (0, "alpha = 1.0: MILP 1.38 vs bound 1.43; rounding 1.25, "
        "greedy 1.23, GA 1.20"),
    (0, "alpha >= 1.2: greedy reaches the bound; MILP joins "
        "by 1.5"),
    (0, "Rounding and GA trail 2.5-8% even at alpha = 2.0 — a "
        "fixed search budget cannot fully recover"),
], left=7.7, width=5.1, top=1.4, size=15)
takeaway(s, "method choice matters most exactly where the "
         "deadline binds; at loose slack almost anything works")

s = add_slide("Q2 — Federation size: capacity buys feasibility, "
              "not accuracy", TEAL, S4, notes=(
    "Two to ten nodes. MILP and greedy on the bound at every "
    "size. GA drifts 1.5% to ~8% below; rounding similar. Extra "
    "nodes enlarge the placement space but the search budget is "
    "fixed — they buy feasible placements, not accuracy."))
pic(s, "perf_nodes_accuracy.png", 0.7, 1.2, width=6.7)
bullets(s, [
    (0, "MILP and greedy match the bound at every N"),
    (0, "GA ~1.5% below bound at N=2 -> ~8% at N=10; rounding "
        "similar"),
    (0, "Placement space grows with N; the search budget does "
        "not"),
], left=7.7, width=5.1, top=1.4, size=15)
takeaway(s, "federation buys feasibility, not accuracy — extra "
         "nodes never lift a method above the bound")

s = add_slide("Q3 — Workflow size: the simple greedy holds up "
              "best", TEAL, S4, notes=(
    "n=10: everyone on the bound. n=100: GA drifts first. "
    "n=1000: MILP past its ~800-variable cap; rounding survives "
    "at ~93 s per re-solve; GA falls to 1.10 in ~159 s. Greedy "
    "stays on the bound in 0.15 s — the only method both fast "
    "and bound-level."))
pic(s, "perf_task_size_accuracy.png", 0.7, 1.2, width=6.7)
bullets(s, [
    (0, "n = 10: all methods on the bound (1.41)"),
    (0, "n = 100: MILP + greedy on bound; GA drifts first "
        "(1.26)"),
    (0, "n = 1000: MILP past its cap; greedy on bound in "
        "0.15 s; rounding ~93 s/LP; GA 1.10 in ~159 s"),
], left=7.7, width=5.1, top=1.4, size=15)
takeaway(s, "at 1000 tasks only the greedy is both fast (0.15 s) "
         "and bound-level — the only scalable accurate method")

s = add_slide("Q4 — Failures: scores stay flat; feasibility is "
              "the story", TEAL, S4, notes=(
    "Retry-once: a failed task reruns in place; accuracy is kept "
    "if the retry still meets the deadline. Scores are flat — "
    "watch feasibility. Greedy stays feasible at every rate "
    "because it finishes early; MILP and GA drop to ~60% at 0.5; "
    "rounding ~20%."))
pic(s, "perf_failure_accuracy.png", 0.7, 1.2, width=6.7)
bullets(s, [
    (0, "Retry-once: failed task reruns in place; accuracy kept "
        "if the retry meets the deadline"),
    (0, "Scores flat — retries preserve accuracy"),
    (0, "Feasibility at rate 0.5: greedy 100%; MILP/GA ~60%; "
        "rounding ~20%"),
    (0, "Greedy finishes early (makespan ~30 vs 40-80) — room "
        "for retries"),
], left=7.7, width=5.1, top=1.4, size=15)
takeaway(s, "under failures the differentiator is feasibility, "
         "not accuracy — early-finish headroom absorbs retries")

s = add_slide("Q5 — Bandwidth degradation: what data-awareness "
              "is worth", TEAL, S4, notes=(
    "Degrade every link to 5% of nominal. The bandwidth-blind "
    "baseline is the cautionary tale: bound-level scores at "
    "every level — but its schedules are late. MILP stays "
    "feasible everywhere; greedy feasible to 0.1x paying "
    "accuracy; GA fails at 0.05x; rounding only above 0.5x."))
pic(s, "perf_bandwidth_accuracy.png", 0.7, 1.2, width=6.7)
bullets(s, [
    (0, "Blind baseline: bound-level scores at every level — "
        "but infeasible (80% at 0.5x, 0% below 0.2x)"),
    (0, "MILP: feasible at all levels, ~10% score loss at "
        "0.05x"),
    (0, "Greedy: feasible to 0.1x paying accuracy; collapses "
        "at 0.05x"),
    (0, "GA holds to 0.1x; rounding survives only above 0.5x"),
], left=7.7, width=5.1, top=1.4, size=15)
takeaway(s, "a scheduler that ignores the links reports a "
         "perfect score on a workflow that finishes late — "
         "high score + late = a missed alert")

s = add_slide("Across datasets: the same story", TEAL, S4, notes=(
    "The per-dataset table agrees. Small: identical scores, "
    "greedy fastest. Medium: greedy's makespan is 43 vs ~61. "
    "Large and xlarge: only greedy and GA fit; greedy holds "
    "~1.41 while the GA falls and pays 20-70 s of search."))
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
    size=13)
takeaway(s, "accuracy is not free in wall time — and neither is "
         "the makespan; the gap widens with scale")

s = add_slide("Structural scale: generation to 10^6 vertices",
              TEAL, S4, notes=(
    "Separately we stress-tested generation: million-task DAGs "
    "in ~3 s with depth growing like log n; million-node "
    "resource graphs in ~7 s. Structural instances only — "
    "honest boundary: schedulable dense instances stop where "
    "constraints and memory do."))
bullets(s, [
    (0, "DAG generator: 10^6 tasks / ~3M edges in 3.1 s; depth "
        "~ log n (24 -> 91 for 10^2 -> 10^6)"),
    (0, "Resource graphs: 10^6 nodes / ~2.4M links in 7.3 s; "
        "avg degree ~5"),
    (0, "Schedulable dense instances stop where constraints "
        "do:"),
    (1, "MILP ~800 assignment vars; LP ~10^5 rows at n=1000"),
], width=6.9)
pic(s, "resource_graphs.png", 7.6, 1.35, width=5.4, base=RES)
caption(s, "Generated federated resource graphs (up to 10^6 "
           "nodes)", 7.6, 6.55, 5.4)

s = add_slide("Honest limits — and what they leave open", TEAL,
              S4, notes=(
    "What we do not claim: the MILP is capped ~800 vars; the LP "
    "grows to ~10^5 rows; the GA has one budget; the failure "
    "model is retry-once-in-place — no resource loss, "
    "replication, or migration. That last limit is the bridge "
    "to the proposal."))
bullets(s, [
    (0, "MILP capped at ~800 assignment variables — deliberate "
        "boundary, not oversight"),
    (0, "LP ~10^5 rows at n=1000; GA uses one fixed budget"),
    (0, "Failure model: retry-once-in-place — no replication, "
        "checkpointing, or migration"),
    (0, "Dense schedulable instances stop near 10^4 tasks; "
        "10^6 experiments are structural"),
    (0, ""),
    (0, "Open: a whole resource fails mid-workflow — the "
        "schedule is decided up front; repair is not"),
], width=12.0)

# ==================================================================
# SECTION 5 — PROPOSED RESEARCH
# ==================================================================
divider("5  |  PROPOSED RESEARCH",
        "Dynamic Partial Repartitioning",
        "Repair the smallest affected region — leave everything "
        "else alone", AMBER, notes=(
    "Section 5 — the proposal itself. Formal problem, research "
    "questions, then the method in depth."))

s = add_slide("The proposal in one line — and its questions",
              AMBER, S5, notes=(
    "The proposal in one callout, then three research questions "
    "that decompose it: the boundary rule, the repair "
    "optimization, and the incremental path update."))
callout(s, "How can we quickly repartition and reschedule only "
        "the affected part of a DAG workflow after a fog "
        "resource fails — reducing recovery time, communication "
        "cost, task movement, and completion time?",
        0.8, 1.3, 11.7, 1.1, PALE, AMBER, 15, bold=True)
bullets(s, [
    (0, "RQ1 — Boundary:  what is the smallest DAG region that "
        "must be repartitioned? (stranded + dependents that "
        "must move)"),
    (0, "RQ2 — Repair:  how to repartition that region to "
        "surviving nodes with minimum recovery cost and the "
        "deadline still met?"),
    (0, "RQ3 — Paths:  how to update communication paths "
        "incrementally instead of recomputing them?"),
], top=2.9, width=12.0, size=16)

s = add_slide("A resource fails mid-workflow", AMBER, S5, notes=(
    "Monitoring detects the failed node. Stranded unfinished "
    "tasks must be rescued; completed work is never redone. The "
    "subtle decision is the boundary: check parents and children "
    "of stranded tasks — sometimes dependents must move too, for "
    "data locality or the deadline."))
# before / after mini infra graphs
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
    (0, "Completed tasks never restart; unaffected tasks never "
        "move"),
    (0, "The boundary question (RQ1): is rescuing the stranded "
        "tasks enough, or must dependents move too?"),
], top=5.3, width=12.0, size=16)

s = add_slide("The method, step by step", AMBER, S5, notes=(
    "Seven steps: initial partition with the existing "
    "schedulers; detect; isolate the stranded set; grow the "
    "minimal affected subgraph under the boundary rule; pick "
    "replacements by capacity and shortest paths to parents and "
    "children; repartition under the recovery cost model; "
    "assign and update only affected paths; resume from the "
    "last good point."))
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
callout(s, "Repartition cost model: added makespan + comm delay "
        "+ data re-shipped + move cost + load balance — under "
        "the deadline", 0.9, 3.8, 11.5, 0.9, PALE, AMBER, 14)
callout(s, "Invariant throughout: completed tasks never "
        "restart, unaffected assignments never move.",
        0.9, 4.9, 11.5, 0.8, PALE, NAVY, 14)

s = add_slide("RQ1 depth — the boundary rule", AMBER, S5, notes=(
    "The technical heart of the proposal. S is mandatory — the "
    "stranded tasks. But dependents may have to move: a child "
    "whose input now crosses a long path, a parent re-shipping "
    "data, a co-located neighbor that loses its locality. The "
    "rule: expand from S while a node fails a stay-test — "
    "deadline slack or data-locality — capped so A stays "
    "minimal. Proving minimality vs 'big enough to repair "
    "well' is RQ1's deliverable."))
bullets(s, [
    (0, "Start:  A = S  (stranded unfinished tasks)"),
    (0, "Expand while some neighbor fails a stay-test:"),
    (1, "deadline test — staying makes its finish exceed the "
        "slack left at tau"),
    (1, "locality test — staying strands its input on a "
        "long path (D/B too large)"),
    (0, "Stop at a cap on |A| or when no neighbor fails a test "
        "— minimality is the claim to verify"),
    (0, "Output:  affected subgraph A with its boundary "
        "dependencies — the only graph we repartition"),
], width=12.0, size=16)

s = add_slide("RQ2 depth — repartitioning the region", AMBER,
              S5, notes=(
    "The repair itself is a smaller instance of the same "
    "optimization family — which is the point: the Part II "
    "schedulers become solvers for the region. Recovery "
    "objective adds movement terms to the accuracy objective; "
    "constraints add 'boundary pins' — interface tasks that "
    "stayed put fix the arrival times the region must respect."))
bullets(s, [
    (0, "Repair is a constrained re-optimization on A — the "
        "Part II schedulers become region solvers"),
    (0, "Objective:  min (added makespan + w1*tasks moved + "
        "w2*data re-shipped) s.t. accuracy and deadline"),
    (0, "Boundary pins:  tasks that stayed fix the data-arrival "
        "times A must respect"),
    (0, "Replacement pool:  surviving nodes with capacity + "
        "short paths to where parents/children live"),
    (0, "Greedy repair first (ms-scale), MILP repair as the "
        "small-region reference"),
], width=12.0, size=16)

s = add_slide("RQ3 depth — incremental path updates", AMBER, S5,
              notes=(
    "Moved tasks need new communication paths to parents and "
    "children. Recomputing all-pairs shortest paths mid-"
    "workflow is too slow — so we reuse dynamic SPT updates "
    "(Riazi, Khanda, Bhowmick et al.): update only the paths "
    "touching the deleted node and the reassigned tasks. That "
    "is what makes partial repair fast enough to matter."))
bullets(s, [
    (0, "Moved tasks need new comm paths to parents and "
        "children"),
    (0, "Recomputing all shortest paths on G_R mid-workflow is "
        "too slow"),
    (0, "Instead: incremental/dynamic SPT update (Riazi, "
        "Bhowmick, Khanda et al.)"),
    (1, "touch only paths through the deleted node and the "
        "moved tasks"),
    (0, "Novel application: dynamic SPT has never driven "
        "workflow repartitioning"),
], width=12.0, size=16)

s = add_slide("What is new — positioning", AMBER, S5, notes=(
    "The pieces exist separately — dynamic path updates, fog "
    "rescheduling, join/leave redistribution, partial "
    "reconsideration — nobody couples them. The novelty is the "
    "two-graph mapping: infra failure to minimal DAG region."))
bullets(s, [
    (0, "Known: dynamic shortest-path updates — never applied "
        "to workflow repartitioning"),
    (0, "Known: fog rescheduling on uncertain events; "
        "redistribution on join/leave"),
    (0, "Known: partial workflow reconsideration — without the "
        "two-graph coupling"),
    (0, ""),
    (0, "New:  infra-node failure -> smallest affected DAG "
        "region -> repartition only that region -> incremental "
        "path update -> resume"),
], width=12.0, size=16)

# ==================================================================
# SECTION 6 — EVALUATION PLAN & TIMELINE
# ==================================================================
divider("6  |  EVALUATION PLAN & TIMELINE",
        "How it will be tested — and when",
        "Baselines, metrics, failure injection, hypotheses, "
        "milestones", AMBER, notes=(
    "Section 6. The evaluation design, then the 12-month plan."))

s = add_slide("Baselines and metrics", AMBER, S6, notes=(
    "Four baselines — complete repartition, greedy rescue, "
    "no-repair static, and MILP on small cases as the quality "
    "reference (Part II's stack supplies it). Metrics cover "
    "speed of recovery, quality of the repaired schedule, and "
    "cost of the disturbance."))
table(s, [
    ["Baselines", "Metrics"],
    ["Complete repartition — reschedule the whole DAG",
     "Recovery time (failure detect -> resume)"],
    ["Greedy rescue — reassign stranded tasks one by one",
     "Workflow completion time / deadline success rate"],
    ["Static — no repair (accuracy of whatever survives)",
     "Communication cost + data re-shipped"],
    ["MILP repair on small cases — the quality reference",
     "Tasks moved; energy; repaired-schedule quality"],
], 0.8, 1.4, 11.7, 3.4, col_widths=[6.2, 5.5], size=13)
takeaway(s, "the Part II platform supplies the baselines and the "
         "failure-injection machinery — the testbed already "
         "exists", accent=TEAL)

s = add_slide("Experiment design — and hypotheses", AMBER, S6,
              notes=(
    "Vary what makes recovery hard: where the failure hits "
    "(critical path vs periphery), how many resources fail at "
    "once, workflow and federation size, and how much slack "
    "remains. The hard case is late failure with little slack. "
    "Three hypotheses, each falsifiable."))
bullets(s, [
    (0, "Failure injection:"),
    (1, "location — critical-path resource vs peripheral"),
    (1, "count — single vs multi-resource failure"),
    (1, "timing — how much deadline slack remains at tau"),
    (0, "Scale: workflow n in {10, 100, 1000}; federation "
        "N in {2 ... 10}"),
    (0, "Hypotheses:"),
    (1, "H1: recovery time << complete repartition, growing "
        "with |A| not |T|"),
    (1, "H2: tasks moved / data re-shipped << baselines at "
        "equal feasibility"),
    (1, "H3: quality stays within x% of MILP repair on small "
        "cases"),
], width=12.0, size=16)

s = add_slide("Timeline — 12 months", AMBER, S6, notes=(
    "Four quarters: build, solve, evaluate, write. Deliverables "
    "land on the existing public repository; the paper targets "
    "the systems venues."))
table(s, [
    ["Months", "Milestone", "Deliverable"],
    ["1-3", "Extend simulator to resource failures; boundary "
     "rule + affected-subgraph extraction; complete-repartition "
     "baseline", "RQ1 implemented; baseline working"],
    ["4-6", "Repartition algorithm + replacement selection; "
     "incremental SPT update", "RQ2 + RQ3 implemented"],
    ["7-9", "Full baseline comparison; MILP reference on small "
     "cases; boundary-rule sensitivity", "H1-H3 tested"],
    ["10-12", "Write the paper; release code on the public "
     "repository; submit", "Paper + artifact"],
], 0.8, 1.4, 11.7, 4.4, col_widths=[1.4, 7.0, 3.3], size=12)

s = add_slide("Risks and mitigations", AMBER, S6, notes=(
    "Three honest risks: the boundary rule might degenerate to "
    "'repartition everything' — mitigated by the cap and the "
    "sensitivity study. Incremental SPT may not pay off at "
    "small graphs — mitigated by measuring the break-even. "
    "Repair quality may trail MILP — mitigated by the "
    "hybrid: greedy for speed, MILP where the region is "
    "small."))
bullets(s, [
    (0, "Risk: boundary rule degenerates to 'repartition "
        "everything'"),
    (1, "mitigate: cap on |A|; sensitivity study vs failure "
        "location and slack"),
    (0, "Risk: incremental SPT does not pay at small graphs"),
    (1, "mitigate: measure the break-even; keep full recompute "
        "as a baseline"),
    (0, "Risk: region repair trails MILP quality"),
    (1, "mitigate: hybrid — greedy repair at scale, MILP "
        "repair for small regions"),
], width=12.0, size=16)

# ==================================================================
# SECTION 7 — CONCLUSION
# ==================================================================
s = add_slide("Conclusion — what this research contributes",
              NAVY, S7, notes=(
    "Three contributions in one line each. A boundary rule for "
    "the smallest affected region. A repartitioning method that "
    "repairs only that region under the recovery cost model. "
    "And the first use of incremental shortest-path updates for "
    "workflow recovery — evaluated against four baselines on "
    "the platform that already exists."))
bullets(s, [
    (0, "Completed:  a proved, data-aware formulation + four "
        "schedulers + a reproducible platform"),
    (0, "Proposed contribution 1:  a principled boundary rule "
        "for the smallest affected DAG region (RQ1)"),
    (0, "Proposed contribution 2:  minimal-region repartitioning "
        "under a recovery cost model (RQ2)"),
    (0, "Proposed contribution 3:  incremental path updates for "
        "workflow recovery (RQ3)"),
    (0, "Expected outcome:  faster recovery with less "
        "disturbance than full repartition, at near-reference "
        "quality"),
    (0, ""),
    (0, "Paper 1 placed the workflow; Paper 2 priced its data "
        "and approximation; Paper 3 keeps it alive when the "
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
