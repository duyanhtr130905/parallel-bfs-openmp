"""Freeze and run an additional in-process BFS comparison on synthetic graphs."""

import argparse
import ctypes
import hashlib
import json
import os
import platform
import random
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import psutil


GRAPHS = [
    dict(id="path513", kind="path", n=513, direction="directed"),
    dict(id="star262k", kind="star", n=262144, direction="directed"),
    dict(id="split-grid", kind="grid", n=32768, direction="undirected", width=128),
    dict(id="ring-random", kind="random", n=350000, direction="directed", degree=6, seed=34178),
    dict(id="layered-overlap", kind="layered", n=393217, direction="directed",
         width=32768, degree=16, seed=39014, overlap=True),
    dict(id="layered-permuted", kind="layered", n=1048577, direction="directed",
         width=65536, degree=8, seed=46029, overlap=False),
]
OMP = ("OMP_DYNAMIC", "OMP_PROC_BIND", "OMP_PLACES", "OMP_WAIT_POLICY",
       "GOMP_CPU_AFFINITY", "OMP_NUM_THREADS", "OMP_THREAD_LIMIT", "OMP_SCHEDULE")
FLAGS = ["-O2", "-Wall", "-Wextra", "-Wpedantic", "-Werror", "-std=c11", "-fopenmp"]
SOURCES = ["src/graph.c", "src/bfs_serial.c", "src/bfs_parallel_basic.c",
           "src/bfs_parallel_optimized.c"]
ROOT = Path(__file__).resolve().parents[1]


def edges(graph):
    n = graph["n"]
    kind = graph["kind"]
    if kind == "path":
        yield from ((v, v + 1) for v in range(n - 1))
    elif kind == "star":
        yield from ((0, v) for v in range(1, n))
    elif kind == "grid":
        width = graph["width"]
        for v in range(n):
            if (v + 1) % width:
                yield v, v + 1
            half_end = (v // (n // 2) + 1) * (n // 2)
            if v + width < half_end:
                yield v, v + width
    elif kind == "random":
        rng = random.Random(graph["seed"])
        for v in range(n):
            successor = (v + 1) % n
            yield v, successor
            for u in rng.sample(range(n - 2), graph["degree"]):
                for excluded in sorted((v, successor)):
                    if u >= excluded:
                        u += 1
                yield v, u
    elif kind == "layered":
        rng = random.Random(graph["seed"])
        width = graph["width"]
        layers = (n - 1) // width
        ids = list(range(1, n))
        rng.shuffle(ids)
        yield from ((0, v) for v in ids[:width])
        for level in range(layers - 1):
            start = level * width
            following = start + width
            shifts = rng.sample(range(1, width), graph["degree"] - 1)
            for i in range(width):
                v = ids[start + i]
                yield v, ids[following + i]
                if graph["overlap"]:
                    candidates = rng.sample(range(width // 8), graph["degree"] - 1)
                    for j in candidates:
                        u = ids[following + (j if j < i else j + 1)]
                        yield v, u
                else:
                    for shift in shifts:
                        yield v, ids[following + (i + shift) % width]
    else:
        raise ValueError(f"Unknown graph kind {kind}")


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


def snapshot():
    battery = psutil.sensors_battery()
    return dict(utc=utc(), cpu_percent=psutil.cpu_percent(interval=1),
                available_bytes=psutil.virtual_memory().available,
                ac=None if battery is None else battery.power_plugged)


def environment():
    qpc_hz = None
    if os.name == "nt":
        frequency = ctypes.c_longlong()
        if ctypes.windll.kernel32.QueryPerformanceFrequency(ctypes.byref(frequency)):
            qpc_hz = frequency.value
    return dict(cpu=os.environ.get("PROCESSOR_IDENTIFIER"), os=platform.platform(),
                physical_cores=psutil.cpu_count(logical=False),
                logical_cores=psutil.cpu_count(),
                os_visible_ram_bytes=psutil.virtual_memory().total,
                python=platform.python_version(), qpc_hz=qpc_hz,
                timer="QPC" if os.name == "nt" else "omp_get_wtime",
                snapshot_sources="psutil cpu_percent, virtual_memory, sensors_battery")


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run(args):
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy()
    for name in OMP:
        env.pop(name, None)
    env["OMP_DYNAMIC"] = "FALSE"
    threads = 8
    timeout = 180
    ram_floor = 2 * 1024**3
    compile_args = ["gcc", *FLAGS, "-Iinclude", "-Isrc", "scripts/benchmark_supplement.c",
                    *SOURCES, "-o"]
    plan = dict(frozen_utc=utc(), graphs=GRAPHS, source=0, schedule="static",
                warmups=2, samples=12, serial_threads=1, omp_threads=threads,
                environment={name: env.get(name) for name in OMP},
                timeout_seconds_per_graph=timeout, minimum_available_bytes=ram_floor,
                order="rotate serial/basic/optimized by round, starting at round -2",
                generator="scripts/run_supplement.py, Python random.Random with recorded seed",
                exclusion="abort and retain files on nonzero exit, timeout, invalid duration, "
                          "distance mismatch or actual team mismatch. No statistical exclusions.",
                dataset_selection="SNAP download unavailable (curl DNS failure). "
                                  "Split grid tests unreachable vertices and undirected CSR. "
                                  "Two layered inputs test duplicate claims and wider frontiers.",
                pilot="none", scaling="not scheduled in this session")
    write_json(out / "plan.json", plan)
    exe = out / ("benchmark.exe" if os.name == "nt" else "benchmark")
    compiler = subprocess.check_output(["gcc", "--version"], text=True).splitlines()[0]
    manifest = dict(baseline_commit=args.commit, started_utc=utc(), compiler=compiler,
                    command=compile_args + [exe.name], host=environment(), before=snapshot(),
                    plan_sha256=digest(out / "plan.json"), source_hashes={
                        name: digest(ROOT / name) for name in [
                            *SOURCES, "src/wall_timer.h", "include/bfs.h", "include/status.h",
                            "include/graph.h", "scripts/run_supplement.py",
                            "scripts/benchmark_supplement.c"]}, graphs={}, complete=False)
    if os.name == "nt":
        runtime = Path(subprocess.check_output(
            ["gcc", "-print-file-name=libgomp-1.dll"], text=True).strip())
        if runtime.is_file():
            manifest["libgomp_sha256"] = digest(runtime)
        power = subprocess.run(["powercfg", "/getactivescheme"], capture_output=True, text=True)
        if power.returncode == 0 and "(" in power.stdout:
            manifest["power_plan"] = power.stdout.rsplit("(", 1)[1].split(")")[0]
    write_json(out / "manifest.json", manifest)
    try:
        subprocess.run([*compile_args, str(exe)], cwd=ROOT, check=True)
        manifest["binary_sha256"] = digest(exe)
        for graph in GRAPHS:
            graph_id, n = graph["id"], graph["n"]
            record = manifest["graphs"][graph_id] = {"before": snapshot()}
            if record["before"]["available_bytes"] < ram_floor:
                raise RuntimeError(f"Available RAM below floor before {graph_id}")
            data = out / f"{graph_id}.edges"
            with data.open("x", encoding="ascii", newline="\n") as handle:
                for m, (v, u) in enumerate(edges(graph), 1):
                    handle.write(f"{v} {u}\n")
            record.update(edge_sha256=digest(data), input_edges=m)
            csv = out / f"{graph_id}.csv"
            profile = out / f"{graph_id}.profile"
            cmd = [str(exe), str(data), str(n), graph["direction"], str(threads)]
            with csv.open("xb") as samples, profile.open("xb") as structure:
                subprocess.run(cmd, stdout=samples, stderr=structure, env=env,
                               timeout=timeout, check=True)
            record.update(csv_sha256=digest(csv), profile_sha256=digest(profile), after=snapshot())
            print(f"{graph_id}: measured {m} input edges", flush=True)
        manifest["complete"] = True
    finally:
        manifest["finished_utc"] = utc()
        manifest["after"] = snapshot()
        write_json(out / "manifest.json", manifest)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output", required=True, type=Path)
    run(parser.parse_args())
