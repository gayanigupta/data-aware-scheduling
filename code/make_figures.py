"""Generate the two conceptual figures for the paper in a clean
draw.io-like style. Figures are drawn at ~print size (single IEEE column,
~3.5 in wide) so the text stays readable at 100% scale.

Outputs into ../Figures/ relative to this script.
Run:  python3 code/make_figures.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "Figures")

BLUE = "#1f78b4"
LT_BLUE = "#dae8fc"
DARK = "#0d2c54"
GREEN = "#d5e8d4"
GREEN_EDGE = "#82b366"
YELLOW = "#fff2cc"
YELLOW_EDGE = "#d6b656"
RED = "#c0392b"
GREY = "#666666"

FS = 10          # main box text
FS_SM = 8        # edge / sub labels
FS_TITLE = 10.5  # section labels


def box(ax, x, y, w, h, text, fc=LT_BLUE, ec=BLUE, fs=FS, dashed=False,
        bold=False):
    b = FancyBboxPatch((x, y), w, h,
                       boxstyle="round,pad=0.02,rounding_size=0.06",
                       linewidth=1.3, edgecolor=ec, facecolor=fc,
                       linestyle="--" if dashed else "-")
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color=DARK,
            fontweight="bold" if bold else "normal", linespacing=1.3)
    return (x + w / 2, y + h / 2)


def arrow(ax, p1, p2, dashed=False, color=DARK, lw=1.4, label=None,
          fs=FS_SM, rad=0.0, label_dx=0.0, label_dy=0.08):
    a = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=12,
                        linewidth=lw, color=color,
                        linestyle="--" if dashed else "-",
                        connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(a)
    if label:
        mx = (p1[0] + p2[0]) / 2 + label_dx
        my = (p1[1] + p2[1]) / 2 + label_dy
        ax.text(mx, my, label, fontsize=fs, ha="center", color=GREY,
                fontstyle="italic")


def figure_architecture():
    # canvas 10 x 7 -> figsize keeps text ~9pt at column width
    fig, ax = plt.subplots(figsize=(4.4, 3.1), dpi=300)
    ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis("off")

    # unreachable cloud
    box(ax, 3.9, 6.05, 2.3, 0.72, "Cloud  (unreachable)",
        fc="#f5f5f5", ec="#aaaaaa", fs=FS_SM, dashed=True)
    ax.plot([4.95, 5.20], [6.28, 6.52], color=RED, lw=1.8)
    ax.plot([5.20, 4.95], [6.28, 6.52], color=RED, lw=1.8)

    # federation boundary
    fed = FancyBboxPatch((0.55, 1.15), 8.9, 4.4,
                         boxstyle="round,pad=0.02,rounding_size=0.12",
                         linewidth=1.4, edgecolor=GREEN_EDGE,
                         facecolor="none", linestyle="--")
    ax.add_patch(fed)
    ax.text(5.0, 5.30, "Federated fog — high-bandwidth inter-fog links",
            ha="center", fontsize=FS_TITLE, color=GREEN_EDGE,
            fontweight="bold")

    # scheduler
    sch = box(ax, 3.5, 4.30, 3.0, 0.78,
              "Data-aware scheduler\nMILP · relaxation · greedy · GA",
              fc=YELLOW, ec=YELLOW_EDGE, fs=FS_SM + 0.5, bold=True)

    # fog nodes
    fgs = {}
    positions = [(1.0, 2.85), (3.2, 2.85), (5.4, 2.85), (7.6, 2.85)]
    for i, (x, y) in enumerate(positions, start=2):
        fgs[i] = box(ax, x, y, 1.5, 0.9, f"FG{i}\nfog node", fs=FS_SM + 0.5)

    # inter-fog links (dashed, bidirectional)
    keys = sorted(fgs)
    for a, b in zip(keys, keys[1:]):
        arrow(ax, (fgs[a][0] + 0.75, fgs[a][1] + 0.06),
              (fgs[b][0] - 0.75, fgs[b][1] + 0.06),
              dashed=True, color=GREY, lw=1.0)
        arrow(ax, (fgs[b][0] - 0.75, fgs[b][1] - 0.06),
              (fgs[a][0] + 0.75, fgs[a][1] - 0.06),
              dashed=True, color=GREY, lw=1.0)
    ax.text(4.3, 3.95, "$B_{ba}$", fontsize=FS_SM, color=GREY,
            fontstyle="italic", ha="center")

    # sensors feeding FG2
    s1 = box(ax, 0.75, 1.35, 2.1, 0.62, "sensors / IoT\npipelines, buoys, drones",
             fc=GREEN, ec=GREEN_EDGE, fs=FS_SM)
    arrow(ax, (s1[0] + 0.3, s1[1] + 0.35), (fgs[2][0] - 0.2, fgs[2][1] - 0.45),
          color=GREEN_EDGE, label="raw data", label_dx=-0.6)

    # scheduler -> fog nodes
    for i in keys:
        arrow(ax, (sch[0] - 1.0 + (i - 2) * 0.67, sch[1] - 0.40),
              (fgs[i][0], fgs[i][1] + 0.47), color=BLUE, lw=1.0,
              rad=0.05 if i % 2 else -0.05)
    ax.text(6.6, 4.0, "$e_{ia}, l_{ia}$", fontsize=FS_SM, color=BLUE,
            fontstyle="italic")

    # database / decision support
    db = box(ax, 6.2, 1.40, 2.9, 0.62,
             "decision support + temporary storage",
             fc=GREEN, ec=GREEN_EDGE, fs=FS_SM)
    arrow(ax, (fgs[5][0], fgs[5][1] - 0.47), (db[0] - 0.4, db[1] + 0.35),
          color=GREEN_EDGE)

    # dead cloud uplink
    arrow(ax, (fgs[4][0], fgs[4][1] + 0.47), (5.05, 6.03), dashed=True,
          color="#aaaaaa", lw=1.1, rad=-0.15)

    fig.savefig(os.path.join(FIG, "federated-fog-architecture.png"),
                bbox_inches="tight", facecolor="white", pad_inches=0.04)
    plt.close(fig)


def figure_dag():
    fig, ax = plt.subplots(figsize=(4.4, 2.9), dpi=300)
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.6); ax.axis("off")

    # tasks (right side)
    T = {}
    T[1] = box(ax, 4.7, 5.05, 2.4, 0.72, "T1  sensor data\ncollection", fs=FS_SM + 0.5)
    T[2] = box(ax, 4.7, 3.55, 2.4, 0.72, "T2  preprocessing +\nfeature extraction", fs=FS_SM + 0.5)
    T[3] = box(ax, 7.7, 4.30, 2.2, 0.72, "T3  disaster simulation\n(spill trajectory)", fs=FS_SM + 0.5)
    T[6] = box(ax, 4.7, 2.05, 2.4, 0.72, "T6  emergency response\ncoordination", fs=FS_SM + 0.5)
    T[5] = box(ax, 7.7, 2.05, 2.2, 0.72, "T5  decision support\n+ planning", fs=FS_SM + 0.5)
    T[4] = box(ax, 7.7, 0.55, 2.2, 0.72, "T4  emergency alerts", fs=FS_SM + 0.5,
               fc=YELLOW, ec=YELLOW_EDGE, bold=True)

    arrow(ax, (T[1][0] - 0.5, T[1][1] - 0.36), (T[2][0] - 0.5, T[2][1] + 0.36),
          label="$D_{12}$", label_dx=-0.3)
    arrow(ax, (T[2][0] + 1.2, T[2][1] + 0.2), (T[3][0] - 0.7, T[3][1] - 0.2),
          label="$D_{23}$", label_dy=0.22, label_dx=-0.15)
    arrow(ax, (T[2][0] + 0.5, T[2][1] - 0.36), (T[6][0] + 0.3, T[6][1] + 0.36),
          label="$D_{26}$", label_dx=-0.35)
    arrow(ax, (T[1][0] + 1.0, T[1][1] - 0.36), (T[6][0] + 0.8, T[6][1] + 0.36),
          label="$D_{16}$", label_dx=0.5, rad=-0.3)
    arrow(ax, (T[3][0], T[3][1] - 0.36), (T[5][0], T[5][1] + 0.36),
          label="$D_{35}$", label_dx=-0.35)
    arrow(ax, (T[6][0] + 1.2, T[6][1]), (T[5][0] - 1.1, T[5][1]),
          label="$D_{65}$", label_dy=0.22)
    arrow(ax, (T[5][0], T[5][1] - 0.36), (T[4][0], T[4][1] + 0.36),
          label="$D_{54}$", label_dx=-0.35)

    # fog nodes (left)
    fgs = {}
    for i, y in enumerate([5.1, 3.8, 2.5, 1.2], start=2):
        fgs[i] = box(ax, 0.55, y, 1.25, 0.6, f"FG{i}", fs=FS_SM + 0.5)
    for a, b in zip([2, 3, 4], [3, 4, 5]):
        arrow(ax, (fgs[a][0], fgs[a][1] - 0.3), (fgs[b][0], fgs[b][1] + 0.3),
              dashed=True, color=GREY, lw=0.9)
    ax.text(1.18, 6.15, "fog nodes\n(links $B_{ba}$)", fontsize=FS_SM,
            ha="center", color=GREY)

    # example assignments (dashed blue)
    for src, dst in [(T[1], fgs[2]), (T[2], fgs[3]), (T[6], fgs[5])]:
        arrow(ax, (src[0] - 1.2, src[1]), (dst[0] + 0.63, dst[1]),
              dashed=True, color=BLUE, lw=1.0)
    ax.text(2.9, 0.30, "dashed blue: assignment $e_{ia}$", fontsize=FS_SM,
            color=BLUE, ha="center", fontstyle="italic")

    fig.savefig(os.path.join(FIG, "disaster-response-dag.png"),
                bbox_inches="tight", facecolor="white", pad_inches=0.04)
    plt.close(fig)


if __name__ == "__main__":
    figure_architecture()
    figure_dag()
    print("wrote federated-fog-architecture.png and disaster-response-dag.png")
