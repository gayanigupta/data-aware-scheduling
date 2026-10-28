"""Generate the two conceptual figures for the paper in a clean
draw.io-like style: Arial text, rounded boxes, lots of whitespace.

Outputs into ../paper/Figures/ relative to this script.
Run:  python3 code/make_figures.py
"""

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["font.family"] = "Arial"
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc, PathPatch
from matplotlib.path import Path
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "paper", "Figures")

BLUE = "#1f78b4"
LT_BLUE = "#dae8fc"
DARK = "#0d2c54"
GREEN = "#d5e8d4"
GREEN_EDGE = "#82b366"
YELLOW = "#fff2cc"
YELLOW_EDGE = "#d6b656"
RED = "#c0392b"
GREY = "#666666"

FS = 9.0         # box text
FS_SM = 8.0      # edge / side labels


def hand_drawn(fn):
    """Run the figure body inside matplotlib's xkcd sketch style with a
    handwriting font, so conceptual figures look hand-drawn."""
    def wrapper():
        with plt.xkcd(randomness=2):
            plt.rcParams["font.family"] = ["Bradley Hand",
                                           "Chalkboard SE",
                                           "Comic Sans MS"]
            return fn()
    return wrapper


def box(ax, x, y, w, h, text, fc=LT_BLUE, ec=BLUE, fs=FS, dashed=False,
        bold=False, square=False):
    style = "square,pad=0.02" if square else \
        "round,pad=0.02,rounding_size=0.12"
    b = FancyBboxPatch((x, y), w, h, boxstyle=style,
                       linewidth=1.2, edgecolor=ec, facecolor=fc,
                       linestyle="--" if dashed else "-")
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color=DARK,
            fontweight="bold" if bold else "normal", linespacing=1.3)
    return (x + w / 2, y + h / 2)


def arrow(ax, p1, p2, dashed=False, color=DARK, lw=1.3, label=None,
          fs=FS_SM, rad=0.0, label_dx=0.0, label_dy=0.12,
          label_color=GREY):
    a = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=11,
                        linewidth=lw, color=color,
                        linestyle="--" if dashed else "-",
                        connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(a)
    if label:
        mx = (p1[0] + p2[0]) / 2 + label_dx
        my = (p1[1] + p2[1]) / 2 + label_dy
        ax.text(mx, my, label, fontsize=fs, ha="center",
                color=label_color, fontstyle="italic",
                bbox=dict(boxstyle="round,pad=0.15", fc="white",
                          ec="none", alpha=0.9))


def figure_architecture():
    """High-level design of the wildfire-response system: sensor inputs
    feed the federated fog network, the data-aware scheduler places the
    six workflow tasks on the four fog nodes, and results return to the
    emergency operations centre.  Landscape layout so it reads well as a
    two-column figure.  Node names, task placements and link rates match
    Fig. 2 exactly."""
    fig, ax = plt.subplots(figsize=(12.0, 6.4), dpi=300)
    ax.set_xlim(0, 34); ax.set_ylim(0, 18.5); ax.axis("off")

    EDGE_BLUE = "#2c7fb8"

    def pill(x, y, text, heavy=False, ha="center"):
        ax.text(x, y, text, fontsize=FS_SM, ha=ha, va="center",
                color=RED if heavy else DARK, zorder=6, linespacing=1.2)

    def elbow(pts, dashed=False, color=DARK, lw=1.1, z=3, ls="-"):
        """Axis-aligned (orthogonal) connector: polyline plus arrowhead
        on the final straight segment."""
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        ax.plot(xs, ys, color=color, lw=lw, zorder=z,
                linestyle=(0, (4, 3)) if dashed else ls)
        a = FancyArrowPatch(pts[-2], pts[-1], arrowstyle="-|>",
                            mutation_scale=11, linewidth=lw,
                            color=color, zorder=z + 1)
        ax.add_patch(a)

    def cloud(x, y, w, h):
        """The classic cloud glyph (Font Awesome outline) scaled to
        (x, y, w, h).  Cubics are already expanded to absolute coords in
        a 640 x 512 box; y is flipped for matplotlib."""
        pts640 = [
            (537.6, 226.6),
            (594.3, 245.5), (633.6, 299.1), (633.6, 362.2),
            (633.6, 440.9), (569.8, 504.9), (491.1, 504.9),
            (160.0, 504.9),
            (71.6, 504.9), (0.0, 433.3), (0.0, 355.4),
            (0.0, 286.3), (50.0, 228.1), (116.5, 215.0),
            (123.2, 139.0), (191.6, 86.3), (270.1, 86.3),
            (331.4, 86.3), (384.6, 125.2), (405.6, 181.6),
            (420.8, 163.3), (446.2, 151.9), (474.2, 151.9),
            (529.7, 151.9), (574.8, 197.0), (574.8, 252.5),
            (574.8, 254.1), (574.7, 255.7), (574.6, 257.2),
            (0, 0),
        ]
        codes = ([Path.MOVETO] + [Path.CURVE4] * 6 + [Path.LINETO] +
                 [Path.CURVE4] * 21 + [Path.CLOSEPOLY])
        pts = [(x + vx / 640.0 * w, y + (512.0 - vy) / 512.0 * h)
               for vx, vy in pts640]
        ax.add_patch(PathPatch(Path(pts, codes), facecolor="white",
                               edgecolor=GREY, lw=1.3, linestyle="--",
                               zorder=4))

    # ---------- top row: inputs and scheduler ----------
    box(ax, 0.8, 15.6, 9.4, 2.3,
        "Wildfire monitoring inputs\ndrone imagery, cameras and\n"
        "environmental sensors", fc="white", ec=DARK, fs=FS,
        square=True)
    box(ax, 12.2, 15.6, 12.2, 2.3,
        "Data-aware scheduler\nassign tasks using compute time,\n"
        "data size and network bandwidth",
        fc="white", ec=DARK, fs=FS, bold=True, square=True)

    # ---------- cloud: unreachable during the event ----------
    cloud(27.3, 13.6, 5.4, 4.3)
    ax.text(30.0, 15.95, "Cloud", ha="center", va="center",
            fontsize=FS, color=DARK, zorder=6)
    ax.plot([28.2, 31.9], [13.9, 17.6], color=RED, lw=1.6,
            solid_capstyle="round", zorder=6)
    ax.text(30.0, 12.85, "unreachable during the event", ha="center",
            va="center", fontsize=FS_SM, color=RED,
            fontstyle="italic", zorder=6)

    # ---------- federated fog container ----------
    fed = FancyBboxPatch((0.8, 1.6), 24.6, 13.0,
                         boxstyle="square,pad=0.02",
                         linewidth=1.3, edgecolor="#9a9a9a",
                         facecolor="none", zorder=0)
    ax.add_patch(fed)
    ax.text(13.1, 14.1, "Federated fog network", ha="center",
            va="center", fontsize=FS + 0.5, color="#555555",
            fontweight="bold", zorder=5)

    # ---------- fog nodes with their Fig. 2 task assignments ----------
    box(ax, 2.2, 9.6, 6.8, 3.6,
        "f1 — Gateway\nT1: Collect data\nT2: Prepare data\n"
        "T3: Detect smoke", fc="white", ec=EDGE_BLUE, fs=FS,
        square=True)
    box(ax, 16.8, 10.0, 6.8, 3.2,
        "f3 — Hospital\nT4: Predict fire spread",
        fc="white", ec=EDGE_BLUE, fs=FS, square=True)
    box(ax, 2.2, 3.2, 6.8, 3.0,
        "f2 — Shelter\nT5: Map fire",
        fc="white", ec=EDGE_BLUE, fs=FS, square=True)
    box(ax, 16.8, 3.2, 6.8, 3.0,
        "f4 — Mobile unit\nT6: Assess damage",
        fc="white", ec=EDGE_BLUE, fs=FS, square=True)

    # ---------- inter-node links (same rates as Fig. 2b) ----------
    # f1 -> f3: straight horizontal, the bottleneck carrying T3 -> T4
    elbow([(9.0, 11.4), (16.8, 11.4)], color=RED, lw=2.0)
    pill(12.9, 12.35, "80 Mbp/s — bottleneck\nT3→T4: 1.8 GB",
         heavy=True)
    # f1 -> f2: straight vertical
    elbow([(5.6, 9.6), (5.6, 6.2)], color="#555555")
    pill(4.9, 7.9, "800 Mbp/s\nT3→T5: 0.9 GB", ha="right")
    # f3 -- f2: present but carries no transfer (dotted, as in Fig. 2b)
    elbow([(20.2, 10.0), (20.2, 7.8), (7.2, 7.8), (7.2, 6.2)],
          color="#555555", ls=":")
    pill(13.6, 8.15, "300 Mbp/s (unused)")
    # f3 -> f4: straight down
    elbow([(21.0, 10.0), (21.0, 6.2)], color="#555555")
    pill(21.7, 8.1, "400 Mbp/s\nT4→T6: 0.35 GB", ha="left")
    # f2 -> f4: straight horizontal
    elbow([(9.0, 4.7), (16.8, 4.7)], color="#555555")
    pill(12.9, 5.15, "500 Mbp/s\nT5→T6: 0.7 GB")

    # ---------- raw data in ----------
    elbow([(3.2, 15.6), (3.2, 13.2)], color=DARK, lw=1.2)
    pill(2.7, 14.75, "Raw data", ha="right")

    # ---------- task placement: dashed, orthogonal drops ----------
    elbow([(13.6, 15.6), (13.6, 14.55), (5.6, 14.55), (5.6, 13.2)],
          dashed=True, color=GREY, lw=0.9, z=2)
    elbow([(18.3, 15.6), (18.3, 13.2)], dashed=True, color=GREY,
          lw=0.9, z=2)
    elbow([(22.9, 15.6), (22.9, 8.6), (4.0, 8.6), (4.0, 6.2)],
          dashed=True, color=GREY, lw=0.9, z=2)
    elbow([(24.0, 15.6), (24.0, 8.95), (18.9, 8.95), (18.9, 6.2)],
          dashed=True, color=GREY, lw=0.9, z=2)
    pill(16.6, 15.1, "Task placement", ha="left")

    # ---------- results out ----------
    box(ax, 27.0, 7.0, 6.4, 3.4,
        "Emergency\noperations centre\nfire map, spread\n"
        "prediction, damage", fc="white", ec=DARK, fs=FS,
        square=True)
    elbow([(23.2, 4.9), (24.7, 4.9), (24.7, 8.7), (27.0, 8.7)],
          color=DARK, lw=1.2)
    pill(24.5, 6.5, "Response results", ha="center")

    ax.text(1.4, 2.0, "Link labels: rate in Mbp/s; task data in GB "
            "where used", fontsize=FS_SM - 0.5, color="#777777",
            fontstyle="italic", ha="left")

    fig.savefig(os.path.join(FIG, "federated-fog-architecture.png"),
                bbox_inches="tight", transparent=True, pad_inches=0.04)
    plt.close(fig)


def figure_dag():
    """Two-panel wildfire-response figure.  Left: the workflow DAG --
    circular task nodes, edges carry realistic data sizes (hundreds of
    MB).  Right: the fog resource network -- rectangular nodes, links
    carry bandwidths in MB/s.  Task colours mark which fog node runs
    them; the highlighted transfer crosses a slow link and pays D/B."""
    NODE_FC = {1: "#dbe9f6", 2: "#e8e4f3", 3: "#dff0e6", 4: "#fdf3d7"}
    EDGE_BLUE = "#2c7fb8"

    fig, ax = plt.subplots(figsize=(7.6, 4.15), dpi=300)
    ax.set_xlim(0, 16.4); ax.set_ylim(0, 9.4); ax.axis("off")

    def tnode(x, y, name, f, r=0.62):
        c = plt.Circle((x, y), r, facecolor=NODE_FC[f],
                       edgecolor=EDGE_BLUE, lw=1.6, zorder=3)
        ax.add_patch(c)
        ax.text(x, y, name, ha="center", va="center", fontsize=9.5,
                color="black", zorder=4, linespacing=1.2)
        return (x, y)

    def fnode(x, y, name, f, w=2.15, h=1.1):
        b = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                           boxstyle="round,pad=0.02,rounding_size=0.18",
                           linewidth=1.6, edgecolor=EDGE_BLUE,
                           facecolor=NODE_FC[f])
        ax.add_patch(b)
        ax.text(x, y, name, ha="center", va="center", fontsize=11,
                color="black", zorder=4, linespacing=1.15)
        return (x, y)

    ax.text(3.5, 9.05, "(a) Wildfire response workflow", ha="center",
            fontsize=14, color="black", fontweight="bold")
    ax.text(11.2, 9.05, "(b) Fog resource network", ha="center",
            fontsize=14, color="black", fontweight="bold")

    # ---------- left: workflow DAG (circles) ----------
    T = {}
    T[1] = tnode(3.5, 7.9, "T1\nCollect\nf1", 1, r=0.82)
    T[2] = tnode(1.4, 5.7, "T2\nPrepare\nf1", 1, r=0.82)
    T[3] = tnode(5.6, 5.7, "T3\nDetect\nf1", 1, r=0.82)
    T[4] = tnode(1.4, 3.3, "T4\nPredict\nf3", 3, r=0.82)
    T[5] = tnode(5.6, 3.3, "T5\nMap\nf2", 2, r=0.82)
    T[6] = tnode(3.5, 1.3, "T6\nAssess\nf4", 4, r=0.82)

    edges = [(1, 2, "1.2 GB", (-0.85, 0.05)), (1, 3, "2.4 GB", (0.9, 0.05)),
             (2, 4, "0.45 GB", (-0.75, 0.05)), (3, 4, "1.8 GB", (0.5, -0.1)),
             (3, 5, "0.9 GB", (0.85, 0.05)), (4, 6, "0.35 GB", (-0.75, 0.05)),
             (5, 6, "0.7 GB", (0.85, 0.05))]
    for a, b, lbl, (dx, dy) in edges:
        heavy = (a, b) == (3, 4)
        ux, uy = T[b][0] - T[a][0], T[b][1] - T[a][1]
        d = math.hypot(ux, uy)
        ux, uy = ux / d, uy / d
        p1 = (T[a][0] + ux * 0.84, T[a][1] + uy * 0.84)
        p2 = (T[b][0] - ux * 0.84, T[b][1] - uy * 0.84)
        arrow(ax, p1, p2,
              color="#c0392b" if heavy else DARK,
              lw=2.0 if heavy else 1.1,
              rad=0.0,
              label=lbl, fs=11,
              label_dx=dx, label_dy=dy,
              label_color="#c0392b" if heavy else "black")

    # ---------- right: resource network (rectangles) ----------
    F = {}
    F[1] = fnode(9.2, 7.6, "f1\nGateway\nedge server + GPU", 1, h=1.55)
    F[2] = fnode(13.2, 7.6, "f2\nShelter\nsmall edge server", 2, h=1.55)
    F[3] = fnode(9.2, 4.2, "f3\nHospital\nedge server + GPU", 3, h=1.55)
    F[4] = fnode(13.2, 4.2, "f4\nMobile unit\nJetson-class", 4, h=1.55)

    # (a, b, label, label offset, directed a -> b?)
    links = [(1, 2, "800 Mbp/s\nWi-Fi 6", (0, -0.75), True, 0),
             (1, 3, "80 Mbp/s\nLTE backup", (-1.45, 0.0), True, 0),
             (2, 4, "500 Mbp/s\nWi-Fi", (1.45, 0.0), True, 0),
             (3, 4, "400 Mbp/s\nWi-Fi", (0.55, 0.72), True, 0)]
    for a, b, lbl, (dx, dy), directed, rot in links:
        heavy = (a, b) == (1, 3)
        if a == 3 and b == 4:                # horizontal, right to right
            p1 = (F[a][0] + 1.05, F[a][1])
            p2 = (F[b][0] - 1.05, F[b][1])
        elif b in (3, 4):                    # vertical, top to bottom
            p1 = (F[a][0], F[a][1] - 0.80)
            p2 = (F[b][0], F[b][1] + 0.80)
        else:                                # horizontal, left to right
            p1 = (F[a][0] + 1.05, F[a][1])
            p2 = (F[b][0] - 1.05, F[b][1])
        col = "#c0392b" if heavy else GREY
        ax.add_patch(FancyArrowPatch(
            p1, p2, arrowstyle="-|>", mutation_scale=13,
            linewidth=2.0 if heavy else 1.1,
            color=col, zorder=2))
        ax.text((p1[0] + p2[0]) / 2 + dx, (p1[1] + p2[1]) / 2 + dy,
                lbl, fontsize=10.5, ha="center", va="center",
                rotation=rot,
                color="#c0392b" if heavy else "black",
                fontstyle="italic", linespacing=1.25, zorder=5,
                bbox=dict(boxstyle="round,pad=0.15", fc="white",
                          ec="none", alpha=0.9))

    # unused f2--f3 link: L-shaped dotted elbow, f2 left edge -> f3 top
    elb = [(12.15, 7.6), (11.6, 7.6), (11.6, 5.0), (9.2, 5.0)]
    xs, ys = zip(*elb)
    ax.plot(xs, ys, color=GREY, lw=1.0, ls=":", zorder=2)
    ax.text(10.6, 6.6, "300 Mbp/s\n(microwave)", fontsize=10.5,
            ha="center",
            va="center", color="black", fontstyle="italic", zorder=5,
            bbox=dict(boxstyle="round,pad=0.15", fc="white",
                      ec="none", alpha=0.9))

    # ---------- line legend ----------
    lx, ly = 14.35, 2.9
    ax.add_patch(FancyArrowPatch((lx, ly + 1.6), (lx + 1.0, ly + 1.6),
        arrowstyle="-|>", mutation_scale=11, linewidth=1.1,
        color=GREY, zorder=5))
    ax.text(lx + 1.2, ly + 1.6, "link in use", fontsize=9,
            va="center", color="black")
    ax.add_patch(FancyArrowPatch((lx, ly + 0.8), (lx + 1.0, ly + 0.8),
        arrowstyle="-|>", mutation_scale=11, linewidth=2.0,
        color="#c0392b", zorder=5))
    ax.text(lx + 1.2, ly + 0.8, "bottleneck", fontsize=9,
            va="center", color="#c0392b")
    ax.plot([lx, lx + 1.0], [ly, ly], color=GREY, lw=1.0, ls=":",
            zorder=5)
    ax.text(lx + 1.2, ly, "unused link", fontsize=9,
            va="center", color="black")

    # ---------- payoff note under the network panel ----------
    ax.text(11.2, 1.85, "Highlighted transfer: T3 on f1 → T4 on f3",
            ha="center", fontsize=10.5, color=DARK, zorder=2)
    ax.text(11.2, 1.4, "Delay = data size / link bandwidth",
            ha="center", fontsize=10, color=DARK, zorder=2)
    ax.text(11.2, 0.85, "1.8 GB = 14.4 Gb / 80 Mbp/s = 180 s",
            ha="center", fontsize=12, color="#c0392b",
            fontweight="bold", zorder=2)

    ax.text(8.2, 0.0,
            "Task colours and fog IDs show placement.   Edge labels: "
            "data sizes.   Link labels: bandwidth.",
            ha="center", va="bottom", fontsize=9.5, color=GREY)

    fig.savefig(os.path.join(FIG, "disaster-response-dag.png"),
                bbox_inches="tight", transparent=True, pad_inches=0.04)
    plt.close(fig)


def figure_pipeline():
    """Method-pipeline flow diagram: inputs on the left, the four
    schedulers sharing one cost model in the middle, and the produced
    schedule + metrics on the right. Sells the paper's story at a glance."""
    fig, ax = plt.subplots(figsize=(6.4, 3.9), dpi=300)
    ax.set_xlim(0, 16); ax.set_ylim(0, 10); ax.axis("off")

    # ---------- inputs ----------
    inp = FancyBboxPatch((0.35, 1.7), 3.7, 7.0,
                         boxstyle="round,pad=0.02,rounding_size=0.15",
                         linewidth=1.0, edgecolor="#8fb8de",
                         facecolor="#f4f9fd")
    ax.add_patch(inp)
    ax.text(2.2, 8.15, "inputs", ha="center", fontsize=FS,
            color="#4a6fa5", fontweight="bold")

    i1 = box(ax, 0.7, 6.35, 3.0, 1.0,
             "workflow DAG\n$D_{ji}$ on every edge", fs=FS)
    i2 = box(ax, 0.7, 4.55, 3.0, 1.0,
             "fog network\n$B_{ba}$ on every link", fs=FS)
    i3 = box(ax, 0.7, 2.75, 3.0, 1.0,
             "$t_{ia}, A_i, P_{ia}$\ndeadline $t_{max}$", fs=FS)

    # ---------- shared cost model + schedulers ----------
    mid = FancyBboxPatch((5.0, 1.7), 6.0, 7.0,
                         boxstyle="round,pad=0.02,rounding_size=0.15",
                         linewidth=1.2, edgecolor=YELLOW_EDGE,
                         facecolor="#fffdf5")
    ax.add_patch(mid)
    ax.text(8.0, 8.15, "one data-aware cost model", ha="center",
            fontsize=FS, color="#8a6d1c", fontweight="bold")
    ax.text(8.0, 7.62, "crossed edge costs $c_{ji}=D_{ji}/B_{ba}$",
            ha="center", fontsize=FS_SM, color=GREY, fontstyle="italic")

    box(ax, 5.45, 6.05, 5.1, 0.85, "MILP  (exact reference)", fs=FS,
        bold=True)
    box(ax, 5.45, 4.95, 5.1, 0.85, "LP + randomized rounding", fs=FS)
    box(ax, 5.45, 3.85, 5.1, 0.85, "bandwidth-aware greedy", fs=FS)
    box(ax, 5.45, 2.75, 5.1, 0.85, "genetic algorithm", fs=FS)
    ax.text(8.0, 2.15, "same objective: max accuracy, meet $t_{max}$",
            ha="center", fontsize=FS_SM, color=GREY, fontstyle="italic")

    # ---------- outputs ----------
    out = FancyBboxPatch((11.95, 1.7), 3.7, 7.0,
                         boxstyle="round,pad=0.02,rounding_size=0.15",
                         linewidth=1.0, edgecolor=GREEN_EDGE,
                         facecolor="#f5faf2")
    ax.add_patch(out)
    ax.text(13.8, 8.15, "schedule", ha="center", fontsize=FS,
            color=GREEN_EDGE, fontweight="bold")

    o1 = box(ax, 12.3, 6.35, 3.0, 1.0,
             "placement $e_{ia}$\nwhich node runs it", fs=FS,
             fc=GREEN, ec=GREEN_EDGE)
    o2 = box(ax, 12.3, 4.55, 3.0, 1.0,
             "fraction $l_{ia}$\nhow much of it runs", fs=FS,
             fc=GREEN, ec=GREEN_EDGE)
    o3 = box(ax, 12.3, 2.75, 3.0, 1.0,
             "score, makespan,\ndeadline feasibility", fs=FS,
             fc=GREEN, ec=GREEN_EDGE)

    # flow arrows
    for src in (i1, i2, i3):
        arrow(ax, (src[0] + 1.5, src[1]), (5.0, src[1]), color=BLUE, lw=1.2)
    for dst in (o1, o2, o3):
        arrow(ax, (11.0, dst[1]), (dst[0] - 1.5, dst[1]), color=GREEN_EDGE,
              lw=1.2)

    fig.savefig(os.path.join(FIG, "scheduling-pipeline.png"),
                bbox_inches="tight", facecolor="white", pad_inches=0.04)
    plt.close(fig)


if __name__ == "__main__":
    figure_architecture()
    figure_dag()
    figure_pipeline()
    print("wrote federated-fog-architecture.png, disaster-response-dag.png, "
          "scheduling-pipeline.png")
