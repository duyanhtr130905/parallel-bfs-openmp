"""Validate saved benchmark runs and regenerate tables and figures."""

import argparse
import csv
import json
import math
from datetime import datetime
from pathlib import Path
from statistics import median, quantiles

from run_supplement import digest, edges

ALGORITHMS = ("serial", "omp-basic", "omp-opt")
LABELS = dict(zip(ALGORITHMS, ("Serial", "Basic", "Optimized")))
CSV_FIELDS = "round,slot,utc,algorithm,requested,actual,ms,bfs_status,validated".split(",")


def load_samples(path, plan):
    groups = {name: [] for name in ALGORITHMS}
    with path.open(newline="", encoding="ascii") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != CSV_FIELDS:
            raise ValueError(f"{path.name}: unexpected CSV schema or time unit")
        rows = list(reader)
    warmups = plan["warmups"]
    expected_count = (warmups + plan["samples"]) * len(ALGORITHMS)
    if len(rows) != expected_count:
        raise ValueError(f"{path.name}: expected exactly {expected_count} rows")
    for row_index, row in enumerate(rows):
        cycle, slot = divmod(row_index, len(ALGORITHMS))
        round_id = cycle - warmups
        algorithm = ALGORITHMS[(cycle + slot) % len(ALGORITHMS)]
        threads = plan["serial_threads" if algorithm == "serial" else "omp_threads"]
        value = float(row["ms"])
        when = datetime.fromisoformat(row["utc"])
        if (None in row or int(row["round"]) != round_id or int(row["slot"]) != slot or
                row["algorithm"] != algorithm or
                int(row["requested"]) != threads or int(row["actual"]) != threads or
                int(row["bfs_status"]) != 0 or int(row["validated"]) != 1 or
                not math.isfinite(value) or value <= 0 or when.utcoffset() is None):
            raise ValueError(f"{path.name}: invalid measurement at CSV line {row_index + 2}")
        if round_id >= 0:
            groups[algorithm].append(value)
    return groups


def load_profile(path, graph, input_edges):
    with path.open(newline="", encoding="ascii") as stream:
        rows = list(csv.reader(stream))
    if (len(rows) < 3 or rows[0][0] != "csr_arcs" or rows[1][0] != "scanned_arcs"):
        raise ValueError(f"{path.name}: missing arc counts or frontier")
    arcs, scanned = (int(row[1]) for row in rows[:2])
    expected_arcs = input_edges * (2 if graph["direction"] == "undirected" else 1)
    width = []
    for i, (name, level, count) in enumerate(rows[2:]):
        if name != "frontier" or int(level) != i or int(count) <= 0:
            raise ValueError(f"{path.name}: invalid frontier level {i}")
        width.append(int(count))
    if arcs != expected_arcs or width[0] != 1 or sum(width) > graph["n"] or not 0 <= scanned <= arcs:
        raise ValueError(f"{path.name}: inconsistent graph profile")
    return arcs, scanned, width


def statistics(values):
    q1, _, q3 = quantiles(values, n=4, method="inclusive")
    return dict(n=len(values), median=median(values), q1=q1, q3=q3, iqr=q3-q1,
                min=min(values), max=max(values))


def summarize(directory):
    plan_file = directory / "plan.json"
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    plan = json.loads(plan_file.read_text(encoding="utf-8"))
    if (not manifest["complete"] or digest(plan_file) != manifest["plan_sha256"] or
            plan["source"] != 0 or plan["schedule"] != "static" or plan["warmups"] != 2 or
            plan["samples"] != 12 or plan["serial_threads"] != 1 or plan["omp_threads"] != 8):
        raise ValueError("Incomplete run or unsupported protocol")
    ids = [graph["id"] for graph in plan["graphs"]]
    if len(set(ids)) != len(ids) or set(ids) != set(manifest["graphs"]):
        raise ValueError("Duplicate or missing graph identifiers")
    result = []
    for graph in plan["graphs"]:
        name = graph["id"]
        record = manifest["graphs"][name]
        csv_path = directory / f"{name}.csv"
        profile_path = directory / f"{name}.profile"
        if digest(csv_path) != record["csv_sha256"] or digest(profile_path) != record["profile_sha256"]:
            raise ValueError(f"{name}: input checksum mismatch")
        m = record["input_edges"]
        arcs, scanned, width = load_profile(profile_path, graph, m)
        samples = load_samples(csv_path, plan)
        stats = {key: statistics(values) for key, values in samples.items()}
        for algorithm, item in stats.items():
            item["speedup"] = stats["serial"]["median"] / item["median"]
            item["efficiency"] = item["speedup"] / (1 if algorithm == "serial" else plan["omp_threads"])
        fastest = min(stats, key=lambda algorithm: stats[algorithm]["median"])
        result.append(dict(**graph, m=m, arcs=arcs, scanned_arcs=scanned, frontier=width,
                           reachable=sum(width), fastest=fastest, stats=stats))
    return result


def tables(results, generated):
    graphs = []
    times = []
    for row in results:
        graph_id = row["id"]
        direction = "Có hướng" if row["direction"] == "directed" else "Vô hướng"
        graphs.append(f"{graph_id} & {direction} & {row['n']} & {row['m']} & {row['reachable']} & "
                      f"{len(row['frontier'])} & {max(row['frontier'])} " + r"\\")
        columns = [f"{row['stats'][name]['median']:.6g}" for name in ALGORITHMS]
        opt = row["stats"]["omp-opt"]
        times.append(" & ".join([graph_id, *columns, f"{opt['speedup']:.3g}",
                                 f"{100 * opt['efficiency']:.3g}", LABELS[row["fastest"]]]) + r" \\")
    for name, rows in [("supplement-graphs", graphs), ("supplement-times", times)]:
        (generated / f"{name}.tex").write_text("\n".join([*rows, r"\bottomrule"]) + "\n",
                                             encoding="utf-8", newline="\n")


def plots(results, figures):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter, MaxNLocator

    plt.rcParams.update({"pdf.fonttype": 42, "font.size": 10})
    fig, axes = plt.subplots(2, figsize=(7.0, 6.0), sharex=True, layout="constrained")
    axes[0].set_yscale("log")
    axes[1].set_yscale("log")
    axes[1].axhline(1, color="0.4", linestyle="--", linewidth=0.8)
    for offset, (name, marker, shade) in enumerate(zip(ALGORITHMS, ("o", "s", "^"), ("0.10", "0.40", "0.65"))):
        stats = [row["stats"][name] for row in results]
        x = [i + (offset - 1) * 0.18 for i in range(len(stats))]
        axes[0].errorbar(x, [s["median"] for s in stats],
                         yerr=[[s["median"] - s["q1"] for s in stats],
                               [s["q3"] - s["median"] for s in stats]],
                         color=shade, marker=marker, linestyle="none", capsize=3, label=LABELS[name])
        if name != "serial":
            axes[1].scatter(x, [s["speedup"] for s in stats], color=shade, marker=marker)
    axes[0].set_ylabel("Thời gian (ms, thang log)")
    axes[1].set_ylabel("Hệ số tăng tốc (thang log)")
    axes[1].set_xticks(range(len(results)), [row["id"] for row in results], rotation=19, ha="right")
    axes[0].legend(ncols=3)
    for ax in axes:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}".replace(".", ",")))
        ax.grid(axis="y", alpha=0.3)
    fig.savefig(figures / "supplement-performance.pdf", metadata={"CreationDate": None})
    plt.close(fig)

    fig, axes = plt.subplots(2, 3, figsize=(7.0, 4.4), layout="constrained")
    for ax, row in zip(axes.flat, results):
        ax.plot(range(len(row["frontier"])), row["frontier"], color="0.2")
        ax.set_title(row["id"])
        ax.set_yscale("log")
        ax.xaxis.set_major_locator(MaxNLocator(nbins=4, integer=True))
        ax.grid(axis="y", alpha=0.3)
    fig.supxlabel("Tầng BFS")
    fig.supylabel("Số đỉnh trong frontier (thang log)")
    fig.savefig(figures / "supplement-frontier.pdf", metadata={"CreationDate": None})
    plt.close(fig)


def structures(figures):
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection

    ring = [(math.cos(i * math.tau / 8), math.sin(i * math.tau / 8)) for i in range(8)]
    grid = [(i % 4, -(i // 4)) for i in range(12)]
    ladder = [(i // 2, -(i % 2)) for i in range(8)]
    binary = [(1.5, 2), (0.5, 1), (2.5, 1), *[(i, 0) for i in range(4)]]
    ternary = [(4, 2), (1, 1), (4, 1), (7, 1), *[(i, 0) for i in range(9)]]
    wide_tiers = [(0, 0), *[(i // 16 + 1, (i % 16 - 7.5) / 3) for i in range(48)]]
    layered = [(0, 0), *[(i // 5 + 1, i % 5 - 2) for i in range(15)]]
    quaternary = [(7.5, 2), *[(i * 4 + 1.5, 1) for i in range(4)],
                  *[(i, 0) for i in range(16)]]
    cases = [
        ("Chu trình", ring, [(i, (i + 1) % 8) for i in range(8)]),
        ("Thang", ladder, [(i, i + 2) for i in range(6)] + [(i, i + 1) for i in range(0, 8, 2)]),
        ("Lưới", grid, [(i, i + 1) for i in range(12) if (i + 1) % 4] +
                       [(i, i + 4) for i in range(8)]),
        ("Cây nhị phân", binary, [((i - 1) // 2, i) for i in range(1, len(binary))]),
        ("Cây bậc ba", ternary, [((i - 1) // 3, i) for i in range(1, len(ternary))]),
        ("Cây bậc bốn", quaternary, [((i - 1) // 4, i) for i in range(1, 21)]),
        ("Đường đi", [(i, 0) for i in range(8)], list(edges(dict(kind="path", n=8)))),
        ("Sao", [(0, 0), *ring], list(edges(dict(kind="star", n=9)))),
        ("Vòng và cung ngẫu nhiên", ring, list(edges(dict(kind="random", n=8, degree=1, seed=34178)))),
        ("Hai lưới tách rời", grid + [(x + 5, y) for x, y in grid],
         list(edges(dict(kind="grid", n=24, width=4)))),
        ("Phân tầng hội tụ", wide_tiers, list(edges(dict(kind="layered", n=49, width=16,
               degree=2, seed=39014, overlap=True)))),
        ("Phân tầng hoán vị", layered, list(edges(dict(kind="layered", n=16, width=5,
               degree=2, seed=46029, overlap=False)))),
    ]
    # Layered generator permutes labels. Locate each vertex by its shuffled tier.
    import random
    fig, axes = plt.subplots(4, 3, figsize=(7, 6.6), layout="constrained")
    for index, (ax, (title, points, pairs)) in enumerate(zip(axes.flat, cases)):
        if index >= 10:
            labels = list(range(1, len(points)))
            random.Random((39014, 46029)[index - 10]).shuffle(labels)
            by_label = dict(zip([0, *labels], points))
            points = [by_label[label] for label in range(len(labels) + 1)]
        ax.add_collection(LineCollection([[points[a], points[b]] for a, b in pairs],
                                         colors="0.5", linewidths=0.85))
        ax.scatter(*zip(*points), color="0.18", s=12, zorder=3)
        ax.scatter(*points[0], color="white", edgecolors="0.12", s=25, zorder=4)
        ax.set_title(title, fontsize=10)
        ax.set_aspect("equal")
        ax.autoscale()
        ax.axis("off")
    fig.savefig(figures / "graph-structures.pdf", metadata={"CreationDate": None})
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("session", type=Path)
    parser.add_argument("--report", type=Path, default=Path("report"))
    args = parser.parse_args()
    results = summarize(args.session)
    generated = args.report / "generated"
    figures = args.report / "figures"
    generated.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    tables(results, generated)
    plots(results, figures)
    structures(figures)
    (args.session / "summary.json").write_text(
        json.dumps(dict(manifest_sha256=digest(args.session / "manifest.json"),
                        analysis_sha256=digest(__file__), results=results), indent=2) + "\n",
        encoding="utf-8", newline="\n")
