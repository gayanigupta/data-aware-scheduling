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
    fig, ax = plt.subplots(figsize=(6.4, 4.4), dpi=300)
    ax.set_xlim(0, 16); ax.set_ylim(0, 11); ax.axis("off")

    # unreachable cloud (crossed out, dashed)
    box(ax, 5.7, 9.85, 4.6, 0.95, "Cloud  (unreachable)",
        fc="#f5f5f5", ec="#aaaaaa", fs=FS, dashed=True)
    cx = (8.0, 10.32)
    ax.plot([cx[0] - 0.18, cx[0] + 0.18], [cx[1] - 0.15, cx[1] + 0.15],
            color=RED, lw=2.0)
    ax.plot([cx[0] + 0.18, cx[0] - 0.18], [cx[1] - 0.15, cx[1] + 0.15],
            color=RED, lw=2.0)

    # federation boundary
    fed = FancyBboxPatch((0.4, 0.7), 15.2, 8.6,
                         boxstyle="round,pad=0.02,rounding_size=0.18",
                         linewidth=1.4, edgecolor=GREEN_EDGE,
                         facecolor="none", linestyle="--")
    ax.add_patch(fed)
    ax.text(8.0, 8.72, "Federated fog — multiple sites share load directly",
            ha="center", fontsize=FS + 0.5, color=GREEN_EDGE,
            fontweight="bold")

    # scheduler
    sch = box(ax, 5.3, 7.05, 5.4, 1.25,
              "Data-aware scheduler\nplaces tasks across the federation",
              fc=YELLOW, ec=YELLOW_EDGE, fs=FS, bold=True)

    # two fog sites (different owners), each with two nodes
    site_a = FancyBboxPatch((0.9, 3.0), 6.6, 3.5,
                            boxstyle="round,pad=0.02,rounding_size=0.15",
                            linewidth=1.0, edgecolor="#8fb8de",
                            facecolor="#f4f9fd", linestyle="-")
    site_b = FancyBboxPatch((8.5, 3.0), 6.6, 3.5,
                            boxstyle="round,pad=0.02,rounding_size=0.15",
                            linewidth=1.0, edgecolor="#8fb8de",
                            facecolor="#f4f9fd", linestyle="-")
    ax.add_patch(site_a); ax.add_patch(site_b)
    ax.text(4.2, 6.10, "fog site A", ha="center", fontsize=FS_SM,
            color="#4a6fa5", fontweight="bold")
    ax.text(11.8, 6.10, "fog site B", ha="center", fontsize=FS_SM,
            color="#4a6fa5", fontweight="bold")

    fgs = {}
    fgs[0] = box(ax, 1.2, 4.45, 2.9, 1.15, "Fog 1\n(base station)", fs=FS)
    fgs[1] = box(ax, 4.3, 4.45, 2.9, 1.15, "Fog 2\n(shelter gateway)", fs=FS)
    fgs[2] = box(ax, 8.8, 4.45, 2.9, 1.15, "Fog 3\n(hospital edge)", fs=FS)
    fgs[3] = box(ax, 12.0, 4.45, 2.9, 1.15, "Fog 4\n(mobile unit)", fs=FS)

    # intra-site links (solid grey) and one cross-site federation link (dashed)
    for a, b in [(0, 1), (2, 3)]:
        arrow(ax, (fgs[a][0] + 1.45, fgs[a][1]), (fgs[b][0] - 1.45, fgs[b][1]),
              color=GREY, lw=0.9)
    arrow(ax, (fgs[1][0] + 1.45, fgs[1][1]), (fgs[2][0] - 1.45, fgs[2][1]),
          dashed=True, color=GREEN_EDGE, lw=1.4)
    ax.text(8.0, 5.35, "inter-site link", fontsize=FS_SM, color=GREEN_EDGE,
            fontstyle="italic", ha="center")

    # scheduler -> fog nodes (assignments)
    for i in range(4):
        arrow(ax, (sch[0] - 1.7 + i * 1.15, sch[1] - 0.50),
              (fgs[i][0], fgs[i][1] + 0.50), color=BLUE, lw=1.0)
    ax.text(11.6, 6.6, "task assignment", fontsize=FS_SM, color=BLUE,
            fontstyle="italic", ha="center")

    # field sensors feeding site A
    s1 = box(ax, 0.9, 1.05, 5.4, 1.2,
             "field sensors\nriver gauges, drones, cameras",
             fc=GREEN, ec=GREEN_EDGE, fs=FS)
    arrow(ax, (s1[0] + 0.5, s1[1] + 0.5), (fgs[0][0] - 0.4, fgs[0][1] - 0.48),
          color=GREEN_EDGE, label="raw data", label_dx=-0.9)

    # results flow to the operations centre
    oc = box(ax, 10.2, 1.05, 5.2, 1.0,
             "emergency operations centre",
             fc=GREEN, ec=GREEN_EDGE, fs=FS)
    arrow(ax, (fgs[3][0], fgs[3][1] - 0.48), (oc[0] + 0.6, oc[1] + 0.5),
          color=GREEN_EDGE, label="results", label_dx=0.9)

    # dead uplink to the cloud
    arrow(ax, (fgs[2][0] + 0.4, fgs[2][1] + 0.48), (8.0, 9.85), dashed=True,
          color="#aaaaaa", lw=1.1)
    ax.text(11.2, 8.45, "uplink down", fontsize=FS_SM, color="#999999",
            fontstyle="italic", ha="left")

    fig.savefig(os.path.join(FIG, "federated-fog-architecture.png"),
                bbox_inches="tight", facecolor="white", pad_inches=0.04)
    plt.close(fig)


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
    T[1] = tnode(3.5, 7.9, "T1\nIngest\n$f_1$", 1)
    T[2] = tnode(1.5, 5.7, "T2\nEnv prep\n$f_1$", 1)
    T[3] = tnode(5.5, 5.7, "T3\nSmoke\ndetect\n$f_1$", 1, r=0.68)
    T[4] = tnode(1.5, 3.3, "T4\nSpread\npredict\n$f_3$", 3)
    T[5] = tnode(5.5, 3.3, "T5\nFire map\n$f_2$", 2)
    T[6] = tnode(3.5, 1.2, "T6\nDamage\nassess\n$f_4$", 4)

    edges = [(1, 2, "200 MB", (-0.75, 0.05)), (1, 3, "800 MB", (0.80, 0.05)),
             (2, 4, "150 MB", (-0.75, 0.05)), (3, 4, "400 MB", (0.45, -0.1)),
             (3, 5, "300 MB", (0.85, 0.05)), (4, 6, "120 MB", (-0.75, 0.05)),
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

    links = [(1, 2, "90 MB/s", (0, 0.14), 0.0),
             (1, 3, "10 MB/s", (-0.95, 0.0), 0.0),
             (2, 4, "60 MB/s", (0.95, 0.0), 0.0),
             (3, 4, "45 MB/s", (0, 0.14), 0.0),
             (2, 3, "30 MB/s", (-0.5, 0.35), 0.0)]
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
    ax.text(12.4, 2.35, "Highlighted transfer: smoke-detection "
            "frames T3 ($f_1$) $\\rightarrow$ spread prediction T4 "
            "($f_3$)", ha="center", fontsize=9, color="#c0392b")
    ax.text(12.4, 1.85, "Delay = data size / link bandwidth",
            ha="center", fontsize=9.5, color="black")
    ax.text(12.4, 1.30, "400 MB / 10 MB/s = 40 s", ha="center",
            fontsize=11, color="#c0392b", fontweight="bold")

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
