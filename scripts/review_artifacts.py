"""Generate combined evidence tables and separate scaling artifacts."""

import argparse
from collections import defaultdict
import csv
from datetime import datetime
import json
import math
from pathlib import Path

from analysis import summarize as historic
from run_scaling import CONFIGS, IDS, REFERENCE, THREADS
from run_supplement import digest
from summarize_supplement import (ALGORITHMS, CSV_FIELDS, LABELS, NAMES, load_profile,
                                  statistics, summarize)

COLORS = ("#555555", "#0072B2", "#D55E00")
MARKERS = ("o", "s", "^")


def table(directory, name, rows):
    body = "\n".join(" & ".join(map(str, row)) + r" \\" for row in rows)
    (directory / f"{name}.tex").write_text(body + "\n\\bottomrule\n", encoding="utf-8", newline="\n")


def comparison(directory):
    meta, samples, _ = historic.load()
    old = {graph: {algo: statistics([float(samples[graph, algo][r]) for r in range(12)])
                   for algo in ALGORITHMS} for graph in meta}
    new = {row["id"]: row["stats"] for row in summarize(REFERENCE)}
    winners = defaultdict(int)
    combined = []
    for day, stats in (("24", old), ("25", new)):
        overview, detail = [], []
        for graph, series in stats.items():
            name = historic.GRAPHS[graph][0] if day == "24" else NAMES[graph]
            medians = [series[algo]["median"] for algo in ALGORITHMS]
            winner = min(ALGORITHMS, key=lambda algo: series[algo]["median"])
            winners[winner] += 1
            overview.append([name, *(f"{value:.6g}" for value in medians),
                             f"{medians[0] / medians[2]:.3g}", LABELS[winner]])
            for algo in ALGORITHMS:
                record = series[algo]
                detail.append([name if algo == "serial" else "", LABELS[algo], record["n"],
                               *(f"{record[key]:.5f}" for key in ("q1", "median", "q3", "iqr", "min", "max"))])
        table(directory, f"statistics-{day}", detail)
        combined.append(r"\textbf{" + day + r"/11/2026} & {} & {} & {} & {} & {} \\")
        combined.extend(" & ".join(row) + r" \\" for row in overview)
        combined.append(r"\midrule" if day == "24" else r"\bottomrule")
    (directory / "comparison.tex").write_text("\n".join(combined) + "\n",
                                              encoding="utf-8", newline="\n")
    return dict(winners)


def scaling_samples(raw):
    groups = defaultdict(list)
    with raw.open(newline="", encoding="ascii") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != CSV_FIELDS:
            raise ValueError(f"{raw.name}: incorrect fields")
        rows = list(reader)
    if len(rows) != 14 * len(CONFIGS):
        raise ValueError(f"{raw.name}: incomplete session")
    for index, row in enumerate(rows):
        cycle, slot = divmod(index, len(CONFIGS))
        algo, threads = CONFIGS[(slot + cycle) % len(CONFIGS)]
        value = float(row["ms"])
        if (None in row or (int(row["round"]), int(row["slot"])) != (cycle - 2, slot)
                or row["algorithm"] != algo or int(row["requested"]) != threads
                or int(row["actual"]) != threads or row["bfs_status"] != "0"
                or row["validated"] != "1" or not math.isfinite(value) or value <= 0
                or datetime.fromisoformat(row["utc"]).utcoffset() is None):
            raise ValueError(f"{raw.name}: invalid sample at row {index + 2}")
        if cycle >= 2:
            groups[algo, threads].append(value)
    result = {key: statistics(values) for key, values in groups.items()}
    baseline = result["serial", 1]["median"]
    for (algo, threads), values in result.items():
        values["speedup"] = baseline / values["median"]
        values["efficiency"] = values["speedup"] / threads
        values["internal"] = result[algo, 1]["median"] / values["median"]
    return result


def scaling(directory):
    plan_path = directory / "plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    reference = json.loads((REFERENCE / "manifest.json").read_text(encoding="utf-8"))
    if (not manifest["complete"] or manifest["plan_sha256"] != digest(plan_path)
            or manifest["reference_manifest_sha256"] != digest(REFERENCE / "manifest.json")
            or tuple(graph["id"] for graph in plan["graphs"]) != IDS
            or set(manifest["graphs"]) != set(IDS) or plan["configurations"] != list(map(list, CONFIGS))
            or (plan["source"], plan["schedule"], plan["warmups"], plan["samples"]) != (0, "static", 2, 12)):
        raise ValueError("Invalid scaling protocol or manifest")
    results = {}
    for graph in plan["graphs"]:
        name = graph["id"]
        info = manifest["graphs"][name]
        raw, profile = (directory / f"{name}.{suffix}" for suffix in ("csv", "profile"))
        if (digest(raw) != info["csv_sha256"] or digest(profile) != info["profile_sha256"]
                or info["edge_sha256"] != reference["graphs"][name]["edge_sha256"]
                or profile.read_bytes().splitlines() != (REFERENCE / profile.name).read_bytes().splitlines()):
            raise ValueError(f"{name}: checksum or structure mismatch")
        load_profile(profile, graph, info["input_edges"])
        results[name] = scaling_samples(raw)
    return results


def scaling_artifacts(results, generated, figures):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    rows = []
    for graph, series in results.items():
        for algo, p in CONFIGS:
            value = series[algo, p]
            measures = [f"{value[key]:.5g}" for key in ("median", "q1", "q3", "iqr", "min", "max")]
            measures.extend([f"{value['speedup']:.3g}", f"{100*value['efficiency']:.3g}",
                             f"{value['internal']:.3g}" if algo != "serial" else ""])
            rows.append([LABELS[algo], p, *(rf"\num{{{v}}}" if v else "--" for v in measures)])
    for index in range(len(IDS)):
        table(generated, f"scaling-detail-{index+1}", rows[11*index:11*(index+1)])
    plt.rcParams.update({"pdf.fonttype": 42, "font.size": 9})
    fig, axes = plt.subplots(3, 3, figsize=(7.2, 6.6), layout="constrained", sharex="col")
    for column, graph in enumerate(IDS):
        axes[0, column].set_title(NAMES[graph])
        for row, key in enumerate(("median", "speedup", "internal")):
            ax = axes[row, column]
            ax.set_yscale("log")
            ax.grid(axis="y", alpha=.3)
            ref = results[graph]["serial", 1]["median"] if row == 0 else 1
            ax.axhline(ref, linestyle="--", color=COLORS[0], linewidth=1,
                       label="Serial" if row != 2 else "OpenMP 1 luồng")
            for algo, color, marker in zip(ALGORITHMS[1:], COLORS[1:], MARKERS[1:]):
                values = [results[graph][algo, p] for p in THREADS]
                y = [v[key] for v in values]
                if row == 0:
                    ax.errorbar(THREADS, y, yerr=[[v["median"]-v["q1"] for v in values],
                                                 [v["q3"]-v["median"] for v in values]],
                                color=color, marker=marker, capsize=2, label=LABELS[algo])
                else:
                    ax.plot(THREADS, y, color=color, marker=marker, label=LABELS[algo])
            ax.set_xticks(THREADS)
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:g}".replace(".", ",")))
    for ax, label in zip(axes[:, 0], ("Thời gian (ms)", "So với Serial", "So với OpenMP 1 luồng")):
        ax.set_ylabel(label)
    axes[0, 2].legend(fontsize=8)
    fig.supxlabel("Số luồng OpenMP")
    fig.savefig(figures / "thread-scaling.pdf", metadata={"CreationDate": None})
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=Path("report"))
    parser.add_argument("--scaling", type=Path)
    args = parser.parse_args()
    generated, figures = (args.report / name for name in ("generated", "figures"))
    for directory in generated, figures:
        directory.mkdir(parents=True, exist_ok=True)
    print(comparison(generated))
    if args.scaling:
        result = scaling(args.scaling)
        scaling_artifacts(result, generated, figures)
        data = {graph: [dict(algorithm=algo, threads=p, **series[algo, p]) for algo, p in CONFIGS]
                for graph, series in result.items()}
        (generated / "scaling-summary.json").write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
