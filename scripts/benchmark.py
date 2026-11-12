"""API v1 benchmark runner. Requires real BFS and matching correctness evidence."""
import argparse
import datetime
import json
import math
import os
from pathlib import Path
import platform
import random
import subprocess
from subprocess import run as execute_binary
import sys
import uuid
from generate_graph import sha256

FIELDS = {"schema_version", "status", "algorithm", "runtime_seconds", "threads_requested",
          "threads_actual", "schedule", "vertices", "edges", "source", "reachable", "directed"}


def strict_json(text):
    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                raise ValueError("duplicate JSON key")
            result[k] = v
        return result
    def constant(value):
        raise ValueError("nonfinite JSON value: " + value)
    return json.loads(text, parse_constant=constant, object_pairs_hook=pairs)


def validate(text, expected=None):
    if len(text.strip().splitlines()) != 1:
        raise ValueError("expected one JSON line")
    r = strict_json(text)
    if not isinstance(r, dict) or set(r) != FIELDS:
        raise ValueError("missing/unknown fields")
    for k in ("schema_version", "threads_requested", "threads_actual", "vertices", "edges", "source", "reachable"):
        if type(r[k]) is not int:
            raise ValueError("integer required: " + k)
    if r["schema_version"] != 1 or r["status"] != "ok":
        raise ValueError("schema/status")
    if r["algorithm"] not in ("serial", "omp-basic", "omp-opt"):
        raise ValueError("algorithm")
    t = r["runtime_seconds"]
    if type(t) not in (int, float) or t < 0 or t > sys.float_info.max or not math.isfinite(t):
        raise ValueError("runtime")
    if not 1 <= r["vertices"] <= 2147483647 or r["edges"] < 0:
        raise ValueError("graph sizes")
    if not 0 <= r["source"] < r["vertices"] or not 1 <= r["reachable"] <= r["vertices"]:
        raise ValueError("source/reachable")
    if any(not 1 <= r[k] <= 2147483647 for k in ("threads_requested", "threads_actual")):
        raise ValueError("threads")
    if type(r["directed"]) is not bool:
        raise ValueError("direction")
    if r["algorithm"] == "serial":
        if r["schedule"] != "none" or r["threads_actual"] != 1:
            raise ValueError("serial metrics")
    elif r["schedule"] not in ("static", "dynamic", "guided"):
        raise ValueError("schedule")
    if expected and any(r[k] != v or type(r[k]) is not type(v) for k, v in expected.items()):
        raise ValueError("inconsistent result metadata")
    return r


def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def run(binary, dataset, environment, evidence, output, threads, repeats=10, seed=2026, timeout=300):
    if repeats < 10 or not threads or any(type(p) is not int or p < 1 for p in threads):
        raise ValueError("need >=10 repeats and positive threads")
    dataset = Path(dataset).resolve()
    meta = strict_json(dataset.read_text(encoding="utf-8"))
    graph = dataset.parent / meta["file"]
    if sha256(graph) != meta["sha256"]:
        raise ValueError("dataset hash mismatch")
    envmeta = strict_json(Path(environment).read_text(encoding="utf-8"))
    required = ("cpu", "physical_cores", "logical_cores", "ram_bytes", "os", "compiler",
                "flags", "openmp", "runtime", "power", "background_load", "source", "reachable")
    if any(k not in envmeta or envmeta[k] in (None, "") for k in required):
        raise ValueError("incomplete verified environment")
    for key in ("physical_cores", "logical_cores", "ram_bytes", "reachable"):
        if type(envmeta[key]) is not int or envmeta[key] < 1:
            raise ValueError("invalid environment integer: " + key)
    if type(envmeta["source"]) is not int or not 0 <= envmeta["source"] < meta["vertices"] or envmeta["reachable"] > meta["vertices"]:
        raise ValueError("invalid source/reachable")
    if max(threads) > envmeta["logical_cores"]:
        raise ValueError("oversubscription")
    head = git("rev-parse", "HEAD")
    proof = strict_json(Path(evidence).read_text(encoding="utf-8"))
    if proof.get("commit") != head or proof.get("status") != "PASS" or not proof.get("command"):
        raise ValueError("correctness evidence must match HEAD")
    evidence_log = Path(proof["log"])
    if not evidence_log.is_file():
        raise ValueError("correctness log missing")
    proof["log_sha256"] = sha256(evidence_log)
    if git("status", "--porcelain"):
        raise ValueError("commit code before official measurements")
    binary = str(Path(binary).resolve())
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path(output) / f"{now}-{head[:8]}-{uuid.uuid4().hex[:8]}"
    out.mkdir(parents=True, exist_ok=False)
    configs = [("serial", 1, "none")] + [(a,p,s) for a in ("omp-basic", "omp-opt")
               for p in sorted(set(threads)) for s in ("static", "dynamic", "guided")]
    rng = random.Random(seed)
    tasks = []
    for repeat in range(-1, repeats):
        order = list(configs)
        rng.shuffle(order)
        tasks.extend((repeat, *c) for c in order)
    manifest = dict(schema_version=1, commit=head, dirty=False, environment=envmeta,
                    dataset=meta, evidence=proof, repeats=repeats, seed=seed, warmups=1,
                    configurations=[dict(algorithm=a, threads_requested=p, schedule=s)
                                    for a,p,s in configs],
                    binary_sha256=sha256(binary), python=sys.version, platform=platform.platform(),
                    runner_sha256=sha256(__file__), invocation=sys.argv, samples=[], hashes={})
    manifest['started_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    manifest['complete'] = False
    manifest["tool_hashes"] = {p.name:sha256(p) for p in Path(__file__).parent.glob("*.py")}
    env = os.environ.copy()
    env["OMP_DYNAMIC"] = "FALSE"
    manifest["omp_environment"] = {k:env.get(k) for k in ("OMP_DYNAMIC", "OMP_PROC_BIND", "OMP_PLACES")}
    failures = 0
    def checkpoint(final=False):
        if final:
            manifest['hashes'] = {f.name:sha256(f) for f in out.iterdir()
                                  if f.name not in ('manifest.json', 'manifest.tmp')}
        temporary = out / 'manifest.tmp'
        temporary.write_text(json.dumps(manifest, indent=2, allow_nan=False)+'\n', encoding='utf-8')
        temporary.replace(out / 'manifest.json')
    checkpoint()
    with (out / "raw.jsonl").open("x", encoding="utf-8") as raw:
        for index, (repeat, algo, p, schedule) in enumerate(tasks):
            cmd = [binary, "--graph", str(graph), "--vertices", str(meta["vertices"]),
                   "--source", str(envmeta["source"]), "--algo", algo, "--threads", str(p),
                   "--schedule", "static" if schedule == "none" else schedule,
                   "--directed" if meta["directed"] else "--undirected"]
            env["OMP_NUM_THREADS"] = str(p)
            item = dict(index=index, repeat=repeat, warmup=repeat == -1, command=cmd,
                        omp_num_threads=p, valid=False)
            item['started_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            stdout, stderr = b"", b""
            try:
                proc = execute_binary(cmd, capture_output=True, timeout=timeout, env=env)
                stdout, stderr = proc.stdout, proc.stderr
                item["exit"] = proc.returncode
                if proc.returncode:
                    raise ValueError("nonzero exit")
                expected = {k:meta[k] for k in ("vertices", "edges", "directed")}
                expected.update(algorithm=algo, threads_requested=p, schedule=schedule,
                                source=envmeta["source"], reachable=envmeta["reachable"])
                result = validate(stdout.decode("utf-8"), expected)
                item["valid"] = True
                item["result"] = result
                if repeat >= 0:
                    raw.write(json.dumps(dict(index=index, result=result), allow_nan=False)+"\n")
                    raw.flush()
            except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
                if isinstance(exc, subprocess.TimeoutExpired):
                    stdout, stderr = exc.stdout or b"", exc.stderr or b""
                item["error"] = str(exc)
                failures += 1
            for suffix, data in (("stdout", stdout), ("stderr", stderr)):
                (out / f"{index:05d}.{suffix}").write_bytes(data)
            manifest["samples"].append(item)
            item['finished_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            checkpoint()
    manifest["complete"] = failures == 0
    manifest['finished_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    checkpoint(final=True)
    return out, failures


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for k in ("binary", "dataset", "environment", "evidence"):
        p.add_argument("--"+k, required=True)
    p.add_argument("--out", default="results/raw")
    p.add_argument("--threads", nargs="+", type=int, required=True)
    p.add_argument("--repeats", type=int, default=10)
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--timeout", type=float, default=300)
    a = p.parse_args()
    directory, errors = run(a.binary, a.dataset, a.environment, a.evidence, a.out, a.threads, a.repeats, a.seed, a.timeout)
    print(directory)
    sys.exit(1 if errors else 0)
