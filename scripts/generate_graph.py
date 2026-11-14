"""Deterministic, streaming edge lists; n/direction live in metadata, not header."""
import argparse
import hashlib
import json
from pathlib import Path


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def generate(out, kind, n=None, rows=None, cols=None, directed=False, max_vertices=1000000):
    if kind == "grid":
        if type(rows) is not int or type(cols) is not int or min(rows, cols) < 1:
            raise ValueError("grid needs positive rows and cols")
        n = rows * cols
    elif kind not in ("path", "star"):
        raise ValueError("unknown graph")
    if type(n) is not int or not 1 <= n <= min(max_vertices, 2147483647):
        raise ValueError("vertex limit exceeded or invalid size")
    # A new directory protects both files, including on partial failure.
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    count = 0
    with (out / "graph.edges").open("x", encoding="ascii", newline="\n") as f:
        for u in range(n):
            if kind == "path":
                targets = [u + 1] if u + 1 < n else []
            elif kind == "star":
                targets = [u] if u > 0 else []
            else:
                targets = []
                if u % cols + 1 < cols:
                    targets.append(u + 1)
                if u + cols < n:
                    targets.append(u + cols)
            for v in targets:
                src = 0 if kind == "star" else u
                f.write(f"{src} {v}\n")
                count += 1
    meta = dict(schema_version=1, kind=kind, vertices=n, rows=rows, cols=cols,
                directed=directed, input_edges=count, edges=count if directed else 2*count,
                file="graph.edges", sha256=sha256(out / "graph.edges"), seed=None,
                provenance="self-generated deterministic path/star/grid; no timing data")
    (out / "dataset.json").write_text(json.dumps(meta, indent=2)+"\n", encoding="utf-8")
    return meta


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("kind", choices=["path", "star", "grid"])
    p.add_argument("--out", required=True)
    p.add_argument("--vertices", type=int)
    p.add_argument("--rows", type=int)
    p.add_argument("--cols", type=int)
    p.add_argument("--directed", action="store_true", help="otherwise loader mirrors edges")
    a = p.parse_args()
    generate(a.out, a.kind, a.vertices, a.rows, a.cols, a.directed)
