"""Regenerate vector figures from the validated CSV and the graph construction."""
from pathlib import Path
import sys

import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
from summarize import ALGORITHMS, GRAPHS, ROOT, load, widths

OUT = ROOT / "report/figures"
COLORS = ["#555555", "#0072B2", "#D55E00"]
HATCHES = ["...", "///", "xx"]
MARKERS = ["o", "s", "^", "D", "v", "P"]


def vi(value):
    return f"{value:g}".replace(".", ",")


def axis_number(value, _position):
    if value >= 1:
        return f"{value:,.0f}".replace(",", "\u2009")
    if 0 < value < 0.001:
        return rf"$10^{{{round(np.log10(value))}}}$"
    return vi(value)


def finish(fig, name):
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight", pad_inches=0.08, metadata={"CreationDate": None})
    plt.close(fig)


def grouped_bars(stats, names, speedup=False):
    fig, ax = plt.subplots(figsize=(6.1, 3.65))
    shifts = [-0.25, 0, 0.25] if not speedup else [0, -0.19, 0.19]
    for i, (algo, label) in enumerate(ALGORITHMS.items()):
        if speedup and algo == "serial":
            continue
        points = np.asarray([stats[g, algo] for g in GRAPHS], dtype=float)
        median = points[:, 1]
        x = np.arange(len(names)) + shifts[i]
        if speedup:
            ratio = np.array([float(stats[g, "serial"][1]) for g in GRAPHS]) / median
            ax.scatter(x, ratio, marker=MARKERS[i], color=COLORS[i], label=label)
        else:
            ax.errorbar(x, median, yerr=[median - points[:, 0], points[:, 2] - median],
                        marker=MARKERS[i], linestyle="none", color=COLORS[i],
                        capsize=3, label=label)
    ax.set_yscale("log")
    ax.set_xticks(range(len(names)), names)
    ax.set_ylabel("Hệ số tăng tốc $S_8$" if speedup else "Thời gian (ms)")
    ax.margins(y=.12)
    if speedup:
        ax.axhline(1, ls="--", color="black", lw=.9, label="$S_8=1$")
    ax.yaxis.set_major_formatter(FuncFormatter(axis_number))
    ax.grid(axis="y", alpha=.26)
    ax.set_axisbelow(True)
    ax.legend(ncols=3, loc="upper center", bbox_to_anchor=(.5, 1.15), frameon=False)
    finish(fig, "speedup" if speedup else "time-iqr")


def layer_figure(metadata):
    fig, axes = plt.subplots(2, 3, figsize=(6.3, 3.9), sharey=True, layout="constrained")
    for i, (graph, ax) in enumerate(zip(GRAPHS, axes.flat)):
        values = widths(graph, metadata[graph][2] + 1)
        end = len(values) - 1
        ax.plot(range(len(values)), values, color="black", lw=1.1, marker=MARKERS[i],
                ms=3, markevery=max(1, end // 6))
        ax.set_yscale("log")
        ax.set_ylim(.72, 5e7)
        ax.set_xticks([0, end // 2, end])
        ax.xaxis.set_major_formatter(FuncFormatter(axis_number))
        ax.set_yticks([1, 100, 10000, 1000000])
        ax.yaxis.set_major_formatter(FuncFormatter(axis_number))
        ax.text(.50, .92, GRAPHS[graph][1], transform=ax.transAxes, ha="center", va="top",
                bbox={"facecolor": "white", "edgecolor": "none", "pad": 1})
        ax.grid(alpha=.25)
    fig.supxlabel("Chỉ số tầng")
    fig.supylabel("Bề rộng tầng (đỉnh)")
    finish(fig, "layer-width")


def serial_samples(samples, stats):
    fig, axes = plt.subplots(1, 2, figsize=(6.1, 2.6), layout="constrained")
    for ax, graph in zip(axes, ("tree2-large", "tree4-large")):
        q1, med, q3 = map(float, stats[graph, "serial"])
        ax.axhspan(q1, q3, color="#eeeeee", label="$[Q_1; Q_3]$")
        ax.axhline(med, ls="--", color=COLORS[0], lw=1)
        ax.scatter(range(12), [float(samples[graph, "serial"][r]) for r in range(12)],
                   color=COLORS[0], marker="o", edgecolors="black", linewidths=.5, zorder=4)
        ax.text(.5, 1.04, GRAPHS[graph][0], ha="center", transform=ax.transAxes)
        ax.set_xticks([0, 2, 4, 5, 7, 9, 11])
        ax.set_xlabel("Vòng đo chính thức")
        ax.yaxis.set_major_formatter(FuncFormatter(axis_number))
        ax.grid(axis="y", alpha=.25)
    axes[0].set_ylabel("Thời gian Serial (ms)")
    finish(fig, "serial-rounds")


def per_layer(metadata, stats):
    graphs = list(GRAPHS)[:3]
    fig, ax = plt.subplots(figsize=(5.9, 2.4), layout="constrained")
    for i, algo in enumerate(("omp-basic", "omp-opt"), 1):
        values = [float(stats[g, algo][1]) / (metadata[g][2] + 1) for g in graphs]
        ax.bar(np.arange(3) + (i - 1.5) * .31, values, width=.29, color=COLORS[i],
               hatch=HATCHES[i], edgecolor="black", linewidth=.5, label=ALGORITHMS[algo])
    ax.set_xticks(range(3), [GRAPHS[g][1] for g in graphs])
    ax.set_ylabel("Thời gian chia cho số tầng (ms/tầng)")
    ax.set_ylim(0, .29)
    ax.yaxis.set_major_formatter(FuncFormatter(axis_number))
    ax.grid(axis="y", alpha=.25)
    ax.set_axisbelow(True)
    ax.legend(frameon=False)
    finish(fig, "per-layer")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5, "pdf.fonttype": 42})
    metadata, samples, stats = load()
    names = ["Chu\ntrình", "Thang", "Lưới", "Cây bậc\nba nhỏ", "Cây nhị\nphân lớn", "Cây bậc\nbốn lớn"]
    grouped_bars(stats, names)
    grouped_bars(stats, names, speedup=True)
    layer_figure(metadata)
    serial_samples(samples, stats)
    per_layer(metadata, stats)


if __name__ == "__main__":
    main()

