"""Generate the two conceptual figures for the paper in a clean
draw.io-like style: Arial text, rounded boxes, lots of whitespace.

Outputs into ../paper/Figures/ relative to this script.
Run:  python3 code/make_figures.py
"""

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["font.family"] = "Arial"
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
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
        bold=False):
    b = FancyBboxPatch((x, y), w, h,
                       boxstyle="round,pad=0.02,rounding_size=0.12",
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
                color=label_color, fontstyle="italic")


def figure_architecture():
    """High-level design of the wildfire-response system: sensor inputs
    feed the federated fog network, the data-aware scheduler places the
    six workflow tasks on the four fog nodes, and results return to the
    emergency operations centre.  Node names, colours, task placements
    and link rates match Fig. 2 exactly."""
    fig, ax = plt.subplots(figsize=(6.4, 8.2), dpi=300)
    ax.set_xlim(0, 16); ax.set_ylim(0, 27.5); ax.axis("off")

    NODE_FC = {1: "#dbe9f6", 2: "#e8e4f3", 3: "#dff0e6", 4: "#fdf3d7"}
    EDGE_BLUE = "#2c7fb8"
    PILL_FC, PILL_EC = "#eaf2fb", EDGE_BLUE

    def pill(x, y, text, heavy=False):
        ax.text(x, y, text, fontsize=FS_SM, ha="center", va="center",
                color=RED if heavy else DARK, zorder=5,
                bbox=dict(boxstyle="round,pad=0.35",
                          fc="#fdecea" if heavy else PILL_FC,
                          ec=RED if heavy else PILL_EC, lw=0.9))

    # ---------- top row: inputs and scheduler ----------
    box(ax, 0.6, 24.9, 6.6, 2.1,
        "Wildfire monitoring inputs\ndrone imagery, cameras and\n"
        "environmental sensors", fs=FS)
    box(ax, 8.6, 24.9, 7.0, 2.1,
        "Data-aware scheduler\nassign tasks using compute time,\n"
        "data size and network bandwidth",
        fc=YELLOW, ec=YELLOW_EDGE, fs=FS, bold=True)

    # ---------- federated fog container ----------
    fed = FancyBboxPatch((1.6, 3.8), 13.0, 20.0,
                         boxstyle="round,pad=0.02,rounding_size=0.18",
                         linewidth=1.4, edgecolor="#9a9a9a",
                         facecolor="#f5f5f5", zorder=0)
    ax.add_patch(fed)
    ax.text(5.4, 23.1, "Federated fog network", ha="center",
            fontsize=FS + 0.5, color="#555555", fontweight="bold")

    # ---------- fog nodes with their Fig. 2 task assignments ----------
    box(ax, 2.4, 19.4, 5.2, 2.9,
        "$f_1$ — Gateway\nT1: Collect data\nT2: Prepare data\n"
        "T3: Detect smoke", fc=NODE_FC[1], ec=EDGE_BLUE, fs=FS)
    box(ax, 9.2, 15.7, 5.0, 2.0,
        "$f_3$ — Hospital\nT4: Predict spread",
        fc=NODE_FC[3], ec=EDGE_BLUE, fs=FS)
    box(ax, 2.8, 11.9, 4.8, 2.0,
        "$f_2$ — Shelter\nT5: Map fire",
        fc=NODE_FC[2], ec=EDGE_BLUE, fs=FS)
    box(ax, 5.4, 7.9, 5.2, 2.0,
        "$f_4$ — Mobile unit\nT6: Assess damage",
        fc=NODE_FC[4], ec=EDGE_BLUE, fs=FS)

    # ---------- inter-node links (same rates as Fig. 2b) ----------
    def link(p1, p2, lbl, lx, ly, heavy=False):
        a = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=11,
                            linewidth=2.0 if heavy else 1.1,
                            color=RED if heavy else "#555555", zorder=3)
        ax.add_patch(a)
        pill(lx, ly, lbl, heavy=heavy)

    link((3.4, 19.4), (4.4, 13.9), "800 Mbps", 2.0, 16.6)             # f1->f2
    link((6.6, 19.4), (9.8, 17.7), "80 Mbps — bottleneck", 9.9, 18.9,
         heavy=True)                                                  # f1->f3
    link((9.6, 15.7), (7.0, 13.9), "300 Mbps", 9.7, 14.7)             # f3->f2
    link((12.8, 15.7), (10.8, 9.9), "400 Mbps", 13.7, 12.7)           # f3->f4
    link((4.8, 11.9), (6.6, 9.9), "500 Mbps", 3.6, 10.8)              # f2->f4

    # ---------- raw data in, task placement, results out ----------
    arrow(ax, (3.8, 24.9), (4.6, 22.3), color=DARK, lw=1.2)
    pill(2.0, 23.9, "Raw data")

    for x0, dst in [(9.8, (6.8, 22.35)), (10.9, (11.6, 17.75)),
                    (12.0, (5.6, 13.95))]:
        arrow(ax, (x0, 24.9), dst, dashed=True, color=GREY, lw=0.9)
    # route the f4 placement arrow down the right edge so it does not
    # cross the f3 box
    ax.plot([14.3, 14.3], [24.9, 10.4], color=GREY, lw=0.9,
            linestyle=(0, (1, 2)), zorder=2)
    arrow(ax, (14.3, 10.4), (10.65, 9.97), dashed=True, color=GREY,
          lw=0.9)
    pill(12.6, 23.9, "Task placement")

    box(ax, 4.8, 0.4, 6.8, 2.1,
        "Emergency operations centre\nfire map, spread prediction\n"
        "and damage assessment", fc=GREEN, ec=GREEN_EDGE, fs=FS)
    arrow(ax, (8.0, 7.9), (8.0, 2.55), color=DARK, lw=1.2)
    pill(9.9, 5.2, "Response results")

    fig.savefig(os.path.join(FIG, "federated-fog-architecture.png"),
                bbox_inches="tight", facecolor="white", pad_inches=0.04)
    plt.close(fig)


@hand_drawn
def figure_dag():
    """Two-panel wildfire-response figure.  Left: the workflow DAG --
    circular task nodes, edges carry realistic data sizes (hundreds of
    MB).  Right: the fog resource network -- rectangular nodes, links
    carry bandwidths in MB/s.  Task colours mark which fog node runs
    them; the highlighted transfer crosses a slow link and pays D/B."""
    NODE_FC = {1: "#dbe9f6", 2: "#e8e4f3", 3: "#dff0e6", 4: "#fdf3d7"}
    EDGE_BLUE = "#2c7fb8"

    fig, ax = plt.subplots(figsize=(10.2, 5.4), dpi=300)
    ax.set_xlim(0, 16.4); ax.set_ylim(0, 9.4); ax.axis("off")

    def tnode(x, y, name, f, r=0.62):
        c = plt.Circle((x, y), r, facecolor=NODE_FC[f],
                       edgecolor=EDGE_BLUE, lw=1.6, zorder=3)
        ax.add_patch(c)
        ax.text(x, y, name, ha="center", va="center", fontsize=8.5,
                color="black", zorder=4, linespacing=1.15)
        return (x, y)

    def fnode(x, y, name, f, w=1.7, h=1.0):
        b = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                           boxstyle="round,pad=0.02,rounding_size=0.18",
                           linewidth=1.6, edgecolor=EDGE_BLUE,
                           facecolor=NODE_FC[f])
        ax.add_patch(b)
        ax.text(x, y, name, ha="center", va="center", fontsize=9,
                color="black", zorder=4, linespacing=1.15)
        return (x, y)

    ax.text(3.5, 9.05, "(a) Wildfire response workflow", ha="center",
            fontsize=11, color="black", fontweight="bold")
    ax.text(12.4, 9.05, "(b) Fog resource network", ha="center",
            fontsize=11, color="black", fontweight="bold")

    # ---------- left: workflow DAG (circles) ----------
    T = {}
    T[1] = tnode(3.5, 7.9, "T1\nCollect\ndata\n$f_1$", 1, r=0.66)
    T[2] = tnode(1.5, 5.7, "T2\nPrepare\ndata\n$f_1$", 1, r=0.66)
    T[3] = tnode(5.5, 5.7, "T3\nDetect\nsmoke\n$f_1$", 1, r=0.68)
    T[4] = tnode(1.5, 3.3, "T4\nPredict\nspread\n$f_3$", 3, r=0.66)
    T[5] = tnode(5.5, 3.3, "T5\nMap\nfire\n$f_2$", 2)
    T[6] = tnode(3.5, 1.2, "T6\nAssess\ndamage\n$f_4$", 4, r=0.66)

    edges = [(1, 2, "250 MB", (-0.75, 0.05)), (1, 3, "1100 MB", (0.85, 0.05)),
             (2, 4, "150 MB", (-0.75, 0.05)), (3, 4, "600 MB", (0.45, -0.1)),
             (3, 5, "300 MB", (0.85, 0.05)), (4, 6, "150 MB", (-0.75, 0.05)),
             (5, 6, "250 MB", (0.85, 0.05))]
    for a, b, lbl, (dx, dy) in edges:
        heavy = (a, b) == (3, 4)
        arrow(ax, (T[a][0], T[a][1] - 0.62), (T[b][0], T[b][1] + 0.62),
              color="#c0392b" if heavy else DARK,
              lw=2.0 if heavy else 1.1,
              rad=-0.10 if abs(a - b) == 2 else 0.0,
              label=lbl, fs=8.5,
              label_dx=dx, label_dy=dy,
              label_color="#c0392b" if heavy else "black")

    # ---------- right: resource network (rectangles) ----------
    F = {}
    F[1] = fnode(10.4, 7.6, "$f_1$\nGateway", 1)
    F[2] = fnode(14.4, 7.6, "$f_2$\nShelter", 2)
    F[3] = fnode(10.4, 4.2, "$f_3$\nHospital", 3)
    F[4] = fnode(14.4, 4.2, "$f_4$\nMobile", 4)

    links = [(1, 2, "800 Mbp/s", (0, 0.14), 0.0),
             (1, 3, "80 Mbp/s", (-1.05, 0.0), 0.0),
             (2, 4, "500 Mbp/s", (1.05, 0.0), 0.0),
             (3, 4, "400 Mbp/s", (0, 0.14), 0.0),
             (2, 3, "300 Mbp/s", (-0.6, 0.4), 0.0)]
    for a, b, lbl, (dx, dy), rad in links:
        heavy = (a, b) == (1, 3)
        if b in (3, 4):
            p1 = (F[a][0], F[a][1] - 0.52)
            p2 = (F[b][0], F[b][1] + 0.52)
        else:
            p1 = (F[a][0] + 0.85, F[a][1])
            p2 = (F[b][0] - 0.85, F[b][1])
        # resource links are undirected: plain lines, no arrowhead
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]],
                color="#c0392b" if heavy else GREY,
                lw=2.0 if heavy else 1.0, zorder=2)
        ax.text((p1[0] + p2[0]) / 2 + dx, (p1[1] + p2[1]) / 2 + dy,
                lbl, fontsize=8.5, ha="center",
                color="#c0392b" if heavy else "black",
                fontstyle="italic")

    # ---------- payoff callout under the network panel ----------
    ax.text(12.4, 2.35, "Highlighted transfer: smoke frames "
            "T3 ($f_1$) $\\rightarrow$ spread prediction T4 "
            "($f_3$)", ha="center", fontsize=9, color="#c0392b")
    ax.text(12.4, 1.85, "Delay = data size / link rate",
            ha="center", fontsize=9.5, color="black")
    ax.text(12.4, 1.30, "600 MB = 4800 Mb,   4800 / 80 Mbp/s "
            "= 60 s", ha="center", fontsize=10.5,
            color="#c0392b", fontweight="bold")

    ax.text(3.5, 0.30,
            "Task colours and fog IDs show placement.  Edge labels: "
            "data size.  Link labels: bandwidth.",
            ha="center", fontsize=8, color="black")

    fig.savefig(os.path.join(FIG, "disaster-response-dag.png"),
                bbox_inches="tight", facecolor="white", pad_inches=0.04)
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
