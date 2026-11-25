"""Plan or run a separate BFS experiment with the fb990bf command-line program."""
import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random
import subprocess
import tempfile

THREADS = (1, 2, 4, 6, 8, 12)
SCHEDULES = ("static", "dynamic", "guided")
ALGORITHMS = ("omp-basic", "omp-opt")
CONFIGS = [("serial", 1, "static")] + [
    (algorithm, threads, schedule)
    for algorithm in ALGORITHMS
    for threads in THREADS
    for schedule in SCHEDULES
]
DATASETS = (("roadNet-CA", False), ("web-Stanford", True))
WARMUPS = 2
REPEATS = 12


def sha256(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def write_json(handle, item):
    print(json.dumps(item, ensure_ascii=False), file=handle, flush=True)


def prepare_graph(source, destination):
    """Translate SNAP identifiers to a dense 0-based interval, preserving all edges."""
    if source.suffix == ".gz":
        contents = gzip.open(source, "rt", encoding="ascii")
    else:
        contents = source.open(encoding="ascii")
    labels = {}
    with contents, destination.open("x", encoding="ascii") as output:
        for number, line in enumerate(contents, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            first, second = line.split()
            labels_on_line = int(first), int(second)
            if min(labels_on_line) < 0:
                raise ValueError(f"Negative node identifier at line {number}")
            u, v = [labels.setdefault(label, len(labels)) for label in labels_on_line]
            print(u, v, file=output)
    if len(labels) < 3:
        raise ValueError(f"{source} has fewer than three distinct endpoints")
    ids = sorted(labels)
    sources = [(ids[i], labels[ids[i]]) for i in (0, len(ids) // 2, len(ids) - 1)]
    return len(labels), sources


def run_case(exe, graph, n, source, directed, config, env):
    algorithm, threads, schedule = config
    args = [
        str(exe), "--graph", str(graph), "--vertices", str(n), "--source", str(source),
        "--algo", algorithm, "--threads", str(threads), "--schedule", schedule,
        "--directed" if directed else "--undirected",
    ]
    result = subprocess.run(args, env=env, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(f"Exit {result.returncode}: {result.stderr.strip()}")
    record = json.loads(result.stdout)
    expected = {
        "schema_version": 1, "status": "ok", "algorithm": algorithm, "source": source,
        "vertices": n, "directed": directed, "threads_actual": threads,
        "threads_requested": threads, "schedule": "none" if algorithm == "serial" else schedule,
    }
    if any(record.get(key) != value for key, value in expected.items()):
        raise ValueError(f"Returned configuration does not match the request: {record}")
    if not math.isfinite(record["runtime_seconds"]) or record["runtime_seconds"] < 0:
        raise ValueError(f"Invalid time: {record}")
    return record


def experiment(exe, inputs, output):
    environment = os.environ.copy()
    environment["OMP_DYNAMIC"] = "FALSE"
    settings = {key: environment.get(key) for key in (
        "OMP_DYNAMIC", "OMP_PROC_BIND", "OMP_PLACES", "OMP_WAIT_POLICY", "GOMP_CPU_AFFINITY"
    )}
    with ExitStack() as stack:
        handle = stack.enter_context(output.open("x", encoding="utf-8"))
        tempdir = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="bfs-extended-")))
        write_json(handle, {
            "type": "session", "utc": datetime.now(timezone.utc).isoformat(),
            "system": platform.platform(), "processor": platform.processor(),
            "binary": str(exe), "binary_sha256": sha256(exe), "omp_environment": settings,
            "warmups": WARMUPS, "repeats": REPEATS, "random_seed": 20261124,
        })
        rng = random.Random(20261124)
        for (name, directed), original in zip(DATASETS, inputs):
            graph = tempdir / f"{name}.edgelist"
            n, sources = prepare_graph(original, graph)
            write_json(handle, {
                "type": "dataset", "graph": name, "source_file": str(original),
                "original_sha256": sha256(original), "remapped_sha256": sha256(graph),
                "vertices": n, "sources": sources, "directed": directed,
            })
            for original_source, source in sources:
                reachable = None
                for repeat in range(-WARMUPS, REPEATS):
                    configs = CONFIGS.copy()
                    rng.shuffle(configs)
                    for turn, config in enumerate(configs):
                        context = {
                            "graph": name, "source_original": original_source,
                            "round": repeat, "position": turn,
                        }
                        try:
                            record = run_case(exe, graph, n, source, directed, config, environment)
                            if reachable is not None and reachable != record["reachable"]:
                                raise ValueError("Reachability differed between configurations")
                            reachable = record["reachable"]
                        except (OSError, RuntimeError, ValueError, KeyError) as exc:
                            write_json(handle, {"type": "error", **context,
                                                "config": config, "message": str(exc)})
                            raise
                        write_json(handle, {"type": "measurement", **record, **context})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="execute the measurements")
    parser.add_argument("--bfs", type=Path, help="compiled BFS CLI from the measurement commit")
    parser.add_argument("--road", type=Path, help="SNAP roadNet-CA edge list, plain text or gzip")
    parser.add_argument("--web", type=Path, help="SNAP web-Stanford edge list, plain text or gzip")
    parser.add_argument("--output", type=Path, help="new JSONL file in an existing directory")
    options = parser.parse_args()
    if not options.run:
        print(json.dumps({"mode": "plan", "datasets": DATASETS, "sources_per_graph": 3,
                          "warmups": WARMUPS, "repeats": REPEATS, "configurations": CONFIGS},
                         indent=2))
        return
    if not (options.bfs and options.road and options.web and options.output):
        parser.error("--run requires --bfs, --road, --web and --output")
    inputs = [path.resolve(strict=True) for path in (options.road, options.web)]
    experiment(options.bfs.resolve(strict=True), inputs, options.output.resolve())


if __name__ == "__main__":
    main()

