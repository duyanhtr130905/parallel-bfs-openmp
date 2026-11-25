"""Run a separate thread-count experiment on byte-verified inputs."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

from run_supplement import (FLAGS, OMP, ROOT, SOURCES, digest, edges,
                            environment, snapshot, utc, write_json)

IDS = ("path513", "ring-random", "layered-permuted")
THREADS = (1, 2, 4, 8, 12)
CONFIGS = [("serial", 1)] + [(algo, p) for algo in ("omp-basic", "omp-opt") for p in THREADS]
REFERENCE = ROOT / "results/experiment-20261125"
RAM_FLOOR = 2 * 1024**3
CPU_CEILING = 65
TIMEOUT = 240


def preflight(samples):
    for _ in range(3):
        item = snapshot()
        samples.append(item)
        if item["available_bytes"] < RAM_FLOOR or item["ac"] is False:
            raise RuntimeError("Insufficient available RAM or running on battery")
        if item["cpu_percent"] <= CPU_CEILING:
            return
    raise RuntimeError("CPU utilization exceeded the predeclared ceiling for three snapshots")


def run(args):
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    previous_plan = json.loads((REFERENCE / "plan.json").read_text(encoding="utf-8"))
    previous = json.loads((REFERENCE / "manifest.json").read_text(encoding="utf-8"))
    if digest(REFERENCE / "plan.json") != previous["plan_sha256"]:
        raise ValueError("Reference plan checksum mismatch")
    graphs = {graph["id"]: graph for graph in previous_plan["graphs"]}
    env = os.environ.copy()
    for name in (*OMP, "GOMP_SPINCOUNT", "OMP_MAX_ACTIVE_LEVELS", "OMP_STACKSIZE"):
        env.pop(name, None)
    env["OMP_DYNAMIC"] = "FALSE"
    plan = dict(utc=utc(), graphs=[graphs[name] for name in IDS], configurations=CONFIGS,
                source=0, schedule="static", warmups=2, samples=12,
                order="Cyclic rotation: index=(slot+round+2) mod 11",
                omp={name: env.get(name) for name in (*OMP, "GOMP_SPINCOUNT",
                     "OMP_MAX_ACTIVE_LEVELS", "OMP_STACKSIZE")},
                affinity="runtime and OS defaults", timeout_seconds_per_graph=TIMEOUT,
                minimum_available_bytes=RAM_FLOOR, cpu_ceiling_percent=CPU_CEILING,
                safety="Abort on RAM/battery failure or three consecutive 1-second snapshots above CPU ceiling",
                exclusion="Abort on invalid time, status, full distance, team size, timeout or input mismatch. No exclusions.")
    write_json(out / "plan.json", plan)
    sources = ["scripts/benchmark_scaling.c", "scripts/run_scaling.py",
               "scripts/run_supplement.py", "src/wall_timer.h", *SOURCES,
               "include/bfs.h", "include/status.h", "include/graph.h"]
    exe = out / ("benchmark.exe" if os.name == "nt" else "benchmark")
    command = ["gcc", *FLAGS, "-Iinclude", "-Isrc", sources[0], *SOURCES, "-o"]
    manifest = dict(baseline_commit=args.commit, started_utc=utc(), host=environment(),
                    compiler=subprocess.check_output(["gcc", "--version"], text=True).splitlines()[0],
                    command=command + [exe.name], plan_sha256=digest(out / "plan.json"),
                    reference_manifest_sha256=digest(REFERENCE / "manifest.json"),
                    source_hashes={name: digest(ROOT / name) for name in sources},
                    before=[], graphs={}, complete=False)
    if os.name == "nt":
        runtime = Path(shutil.which("gcc")).with_name("libgomp-1.dll")
        if runtime.is_file():
            manifest["libgomp_sha256"] = digest(runtime)
        power = subprocess.run(["powercfg", "/getactivescheme"], capture_output=True, text=True)
        if power.returncode == 0 and "(" in power.stdout:
            manifest["power_plan"] = power.stdout.rsplit("(", 1)[1].split(")")[0]
    try:
        preflight(manifest["before"])
        subprocess.run([*command, str(exe)], cwd=ROOT, check=True)
        manifest["binary_sha256"] = digest(exe)
        for graph_id in IDS:
            graph = graphs[graph_id]
            record = manifest["graphs"][graph_id] = {"before": []}
            data = out / f"{graph_id}.edges"
            with data.open("x", encoding="ascii", newline="\n") as handle:
                for m, (v, u) in enumerate(edges(graph), 1):
                    handle.write(f"{v} {u}\n")
            record.update(edge_sha256=digest(data), input_edges=m)
            reference = previous["graphs"][graph_id]
            if any(record[key] != reference[key] for key in ("input_edges", "edge_sha256")):
                raise ValueError(f"{graph_id}: input differs from the published session")
            preflight(record["before"])
            raw = out / f"{graph_id}.csv"
            profile = out / f"{graph_id}.profile"
            cmd = [str(exe), str(data), str(graph["n"]), graph["direction"]]
            with raw.open("xb") as csv, profile.open("xb") as structure:
                subprocess.run(cmd, stdout=csv, stderr=structure, env=env, timeout=TIMEOUT, check=True)
            record.update(csv_sha256=digest(raw), profile_sha256=digest(profile), after=snapshot())
            if profile.read_bytes().splitlines() != (REFERENCE / profile.name).read_bytes().splitlines():
                raise ValueError(f"{graph_id}: profile differs from the published session")
            print(f"{graph_id}: finished, complete distance arrays and teams checked", flush=True)
        manifest["complete"] = True
    except Exception as error:
        manifest["failure"] = type(error).__name__
        raise
    finally:
        manifest.update(finished_utc=utc(), after=snapshot())
        write_json(out / "manifest.json", manifest)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output", required=True, type=Path)
    run(parser.parse_args())
