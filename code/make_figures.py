"""Generate the two conceptual figures for the paper in a clean
draw.io-like style: Arial text, rounded boxes, lots of whitespace.

Outputs into ../Figures/ relative to this script.
Run:  python3 code/make_figures.py
"""

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["font.family"] = "Arial"
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

FS = 7.0         # box text
FS_SM = 6.5      # edge / side labels


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
          fs=FS_SM, rad=0.0, label_dx=0.0, label_dy=0.12):
    a = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=11,
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
    fig, ax = plt.subplots(figsize=(6.4, 4.4), dpi=300)
    ax.set_xlim(0, 16); ax.set_ylim(0, 11); ax.axis("off")

    # unreachable cloud (crossed out, dashed)
    box(ax, 6.3, 9.9, 3.4, 0.85, "Cloud  (unreachable)",
        fc="#f5f5f5", ec="#aaaaaa", fs=FS, dashed=True)
    cx = (8.0, 10.32)
    ax.plot([cx[0] - 0.14, cx[0] + 0.14], [cx[1] - 0.12, cx[1] + 0.12],
            color=RED, lw=2.0)
    ax.plot([cx[0] + 0.14, cx[0] - 0.14], [cx[1] - 0.12, cx[1] + 0.12],
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
    sch = box(ax, 5.7, 7.15, 4.6, 0.95,
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
    fgs[0] = box(ax, 1.4, 4.55, 2.4, 0.9, "Fog 1\n(base station)", fs=FS)
    fgs[1] = box(ax, 4.6, 4.55, 2.4, 0.9, "Fog 2\n(shelter gateway)", fs=FS)
    fgs[2] = box(ax, 9.0, 4.55, 2.4, 0.9, "Fog 3\n(hospital edge)", fs=FS)
    fgs[3] = box(ax, 12.2, 4.55, 2.4, 0.9, "Fog 4\n(mobile unit)", fs=FS)

    # intra-site links (solid grey) and one cross-site federation link (dashed)
    for a, b in [(0, 1), (2, 3)]:
        arrow(ax, (fgs[a][0] + 1.2, fgs[a][1]), (fgs[b][0] - 1.2, fgs[b][1]),
              color=GREY, lw=0.9)
    arrow(ax, (fgs[1][0] + 1.2, fgs[1][1]), (fgs[2][0] - 1.2, fgs[2][1]),
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
    s1 = box(ax, 0.9, 1.15, 4.0, 0.95,
             "field sensors\nriver gauges, drones, cameras",
             fc=GREEN, ec=GREEN_EDGE, fs=FS)
    arrow(ax, (s1[0] + 0.5, s1[1] + 0.5), (fgs[0][0] - 0.4, fgs[0][1] - 0.48),
          color=GREEN_EDGE, label="raw data", label_dx=-0.9)

    # results flow to the operations centre
    oc = box(ax, 10.6, 1.15, 5.0, 0.95,
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
    fig, ax = plt.subplots(figsize=(6.4, 4.6), dpi=300)
    ax.set_xlim(0, 16); ax.set_ylim(0, 12); ax.axis("off")

    # workflow DAG, top to bottom: two data sources join, work splits into
    # a forecast branch and a planning branch, then merges.
    # plain-language labels -- the formal D_ji / e_ia notation stays in the
    # paper text and caption
    T = {}
    T[1] = box(ax, 4.9, 10.9, 3.4, 0.85, "T1  collect\nsensor data", fs=FS)
    T[2] = box(ax, 10.0, 10.9, 3.4, 0.85, "T2  get aerial &\nsatellite photos", fs=FS)
    T[3] = box(ax, 4.9, 8.55, 3.4, 0.85, "T3  combine &\nclean data", fs=FS)
    T[4] = box(ax, 10.0, 8.55, 3.4, 0.85, "T4  assess\ndamage", fs=FS)
    T[5] = box(ax, 4.9, 6.20, 3.4, 0.85, "T5  forecast\nimpact", fs=FS)
    T[6] = box(ax, 10.0, 6.20, 3.4, 0.85, "T6  plan evacuation\n& supplies", fs=FS)
    T[7] = box(ax, 7.45, 3.85, 3.4, 0.85, "T7  coordinate\nresponse", fs=FS)
    T[8] = box(ax, 7.45, 1.55, 3.4, 0.85, "T8  send emergency\nalerts", fs=FS,
               fc=YELLOW, ec=YELLOW_EDGE, bold=True)

    arrow(ax, (T[1][0] - 0.2, T[1][1] - 0.43), (T[3][0] - 0.2, T[3][1] + 0.43))
    arrow(ax, (T[2][0] - 0.6, T[2][1] - 0.43), (T[3][0] + 0.8, T[3][1] + 0.43))
    arrow(ax, (T[2][0], T[2][1] - 0.43), (T[4][0], T[4][1] + 0.43))
    arrow(ax, (T[3][0], T[3][1] - 0.43), (T[5][0], T[5][1] + 0.43))
    arrow(ax, (T[3][0] + 0.9, T[3][1] - 0.43), (T[6][0] - 0.6, T[6][1] + 0.43))
    arrow(ax, (T[4][0], T[4][1] - 0.43), (T[6][0] + 0.2, T[6][1] + 0.43))
    # cross edges between the two branches
    arrow(ax, (T[4][0] - 1.2, T[4][1] - 0.43), (T[5][0] + 1.0, T[5][1] + 0.43))
    arrow(ax, (T[5][0] + 1.7, T[5][1] + 0.15), (T[6][0] - 1.7, T[6][1] + 0.15))
    arrow(ax, (T[5][0] + 0.7, T[5][1] - 0.43), (T[7][0] - 0.7, T[7][1] + 0.43))
    arrow(ax, (T[6][0] - 0.7, T[6][1] - 0.43), (T[7][0] + 0.7, T[7][1] + 0.43))
    arrow(ax, (T[7][0], T[7][1] - 0.43), (T[8][0], T[8][1] + 0.43))
    ax.text(14.0, 9.9, "arrows carry data\nbetween tasks",
            fontsize=FS_SM, color=GREY, fontstyle="italic", ha="right")

    # fog nodes (left column)
    fgs = {}
    for i, y in enumerate([9.7, 7.5, 5.3, 3.1]):
        fgs[i] = box(ax, 0.7, y, 1.6, 0.75, f"Fog {i+1}", fs=FS)
    for a, b in zip([0, 1, 2], [1, 2, 3]):
        arrow(ax, (fgs[a][0], fgs[a][1] - 0.38), (fgs[b][0], fgs[b][1] + 0.38),
              dashed=True, color=GREY, lw=0.9)
    ax.text(1.5, 11.3, "fog nodes\n(local network)", fontsize=FS_SM,
            ha="center", color=GREY)

    # example assignments (dashed blue, task -> node)
    for src, dst in [(T[1], fgs[0]), (T[3], fgs[1]), (T[7], fgs[2])]:
        arrow(ax, (src[0] - 1.7, src[1]), (dst[0] + 0.8, dst[1]),
              dashed=True, color=BLUE, lw=1.0)
    ax.text(1.5, 0.7, "dashed blue =\nwhere tasks run", fontsize=FS_SM,
            color=BLUE, ha="center", fontstyle="italic")

    fig.savefig(os.path.join(FIG, "disaster-response-dag.png"),
                bbox_inches="tight", facecolor="white", pad_inches=0.04)
    plt.close(fig)


if __name__ == "__main__":
    figure_architecture()
    figure_dag()
    print("wrote federated-fog-architecture.png and disaster-response-dag.png")
